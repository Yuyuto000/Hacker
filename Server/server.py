import os
import subprocess
import json
from flask import Flask, request, jsonify, send_file
from vpn_manager import configure_vpn, restart_vpn
from proxy_manager import configure_proxy, restart_proxy

# 設定ファイル読み込み
CONFIG_FILE = "config.json"
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# サーバー設定
COMMANDS_DIR = "./commands"
LOGS_DIR = "./logs"
os.makedirs(COMMANDS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Flaskサーバー初期化
app = Flask(__name__)

@app.route("/")
def index():
    return "ハッキングサーバーが稼働中です。", 200

@app.route("/vpn/restart", methods=["POST"])
def restart_vpn_route():
    restart_vpn(config["vpn_config"])
    return jsonify({"message": "VPN再起動成功"}), 200

@app.route("/proxy/restart", methods=["POST"])
def restart_proxy_route():
    restart_proxy(config["proxy_config"])
    return jsonify({"message": "プロキシ再起動成功"}), 200

@app.route("/upload", methods=["POST"])
def upload_script():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    script = request.files["file"]
    script_path = os.path.join(COMMANDS_DIR, script.filename)
    script.save(script_path)
    return jsonify({"message": f"{script.filename} がアップロードされました。"}), 200

@app.route("/execute", methods=["POST"])
def execute_script():
    data = request.json
    if not data or "filename" not in data:
        return jsonify({"error": "Filename not provided"}), 400
    script_path = os.path.join(COMMANDS_DIR, data["filename"])
    if not os.path.exists(script_path):
        return jsonify({"error": f"{data['filename']} が見つかりません。"}), 404
    log_file = os.path.join(LOGS_DIR, f"{data['filename']}.log")
    with open(log_file, "w") as log:
        subprocess.run(["bash", script_path], stdout=log, stderr=subprocess.STDOUT)
    return jsonify({"message": f"{data['filename']} を実行しました。", "log": log_file}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
