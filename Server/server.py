import os
import subprocess
import json
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, send
from vpn_manager import configure_vpn, restart_vpn
from proxy_manager import configure_proxy, restart_proxy
from firewall_manager import configure_firewall
from ssl_setup import setup_ssl
from dashboard_manager import init_dashboard
from automation_manager import execute_script, list_scripts
import asyncio

# 設定ファイル読み込み
CONFIG_FILE = "config.json"
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# ディレクトリ作成
COMMANDS_DIR = "./commands"
LOGS_DIR = "./logs"
TOOLS_DIR = "./NormalTools"
os.makedirs(TOOLS_DIR, exist_ok=True)
os.makedirs(COMMANDS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Flaskアプリ初期化
app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet")
init_dashboard(app)

# 非同期ログ収集
async def tail_logs():
    log_file = os.path.join(LOGS_DIR, "server.log")
    async with aiofiles.open(log_file, mode="a") as log:
        process = await asyncio.create_subprocess_exec(
            "tail", "-f", "/var/log/syslog",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        async for line in process.stdout:
            await log.write(line.decode())
        await process.wait()

# 非同期エンドポイント用にrun_in_executorを追加
async def run_command_async(command):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, os.popen, command)

# クライアントからのチャットメッセージを非同期で受信
@socketio.on("message")
async def handle_message(message):
    print(f"受信したメッセージ: {message}")
    await save_message(message)  # 非同期でメッセージを保存
    send(message, broadcast=True)

# メッセージをファイルに保存
async def save_message(message):
    log_file = os.path.join(LOGS_DIR, "chat_log.txt")
    async with aiofiles.open(log_file, mode="a") as f:
        await f.write(message + "\n")

# エンドポイント（VPN, プロキシ, ファイアウォール）
@app.route("/vpn/restart", methods=["POST"])
def restart_vpn_route():
    restart_vpn(config["vpn_config"])
    return jsonify({"message": "VPN再起動成功"}), 200

@app.route("/proxy/restart", methods=["POST"])
def restart_proxy_route():
    restart_proxy(config["proxy_config"])
    return jsonify({"message": "プロキシ再起動成功"}), 200

@app.route("/firewall/configure", methods=["POST"])
def configure_firewall_route():
    rules = request.json.get("rules", [])
    configure_firewall(rules)
    return jsonify({"message": "ファイアウォールを更新しました。"}), 200

@app.route("/script_execute", methods=["POST"])
async def script_execute():
    if "file" not in request.files:
        return jsonify({"error": "スクリプトファイルがアップロードされていません"}), 400
    
    script = request.files["file"]
    script_path = os.path.join(COMMANDS_DIR, script.filename)
    
    # スクリプトをアップロード
    script.save(script_path)
    
    # スクリプト実行
    log_file = os.path.join(LOGS_DIR, f"{script.filename}.log")
    async with aiofiles.open(log_file, mode="w") as log:
        process = await asyncio.create_subprocess_exec(
            "bash", script_path,
            stdout=log,
            stderr=asyncio.subprocess.PIPE
        )
        stderr_output = await process.stderr.read()
        await log.write(stderr_output.decode())
        await process.wait()
    
    # 実行結果に基づくレスポンス
    status = "success" if process.returncode == 0 else "error"
    
    # 実行結果とログを返す
    response = {
        "message": f"{script.filename} の実行が完了しました。",
        "status": status,
        "log": log_file
    }
    
    # スクリプトを削除
    os.remove(script_path)
    
    return jsonify(response), 200

# ツールの実行
async def execute_tool(tool_name, params):
    tool_path = os.path.join(TOOLS_DIR, f"{tool_name}.json")
    if not os.path.exists(tool_path):
        return {"error": f"ツール '{tool_name}' が見つかりません。"}

    async with aiofiles.open(tool_path, mode="r") as f:
        tool_data = json.load(await f.read())

    # コマンド実行
    command = tool_data.get("command")
    if not command:
        return {"error": "ツールにコマンドが定義されていません。"}

    # パラメータを追加
    for key, value in params.items():
        command = command.replace(f"{{{key}}}", str(value))

    # 実行結果を格納
    result = await run_command_async(command)
    return {"message": "ツールの実行が成功しました。", "output": result}

# エンドポイント
@app.route("/tools", methods=["GET"])
async def list_tools():
    tools = get_tool_list()
    return jsonify(tools), 200

@app.route("/tools/execute", methods=["POST"])
async def run_tool():
    data = await request.get_json()
    tool_name = data.get("tool_name")
    params = data.get("params", {})

    if not tool_name:
        return jsonify({"error": "ツール名が指定されていません。"}), 400

    result = await execute_tool(tool_name, params)
    return jsonify(result), 200

if __name__ == "__main__":
    setup_ssl()
    # 非同期ログ収集の開始
    loop = asyncio.get_event_loop()
    loop.create_task(tail_logs())

    # WebSocketでサーバーを起動
    socketio.run(app, host="0.0.0.0", port=5000, ssl_context=("cert.pem", "key.pem"))
