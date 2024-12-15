import os
import subprocess
import requests
import json
import websocket
import tkinter as tk
from tkinter import (
    Toplevel, Button, Entry, Text, Label, filedialog, messagebox
)
from tkinter.scrolledtext import ScrolledText
from threading import Thread

# サーバーURLとエンドポイント設定
SERVER_URL = "http://localhost:5000"
WEBSOCKET_URL = "ws://localhost:5000/socket.io/"

# サーバー上のツールリストを取得
def fetch_tool_list():
    try:
        response = requests.get(f"{SERVER_URL}/tools", verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("エラー", "ツールリストの取得に失敗しました。")
            return []
    except requests.exceptions.RequestException as e:
        messagebox.showerror("エラー", f"通信エラー: {str(e)}")
        return []

# ===== WebSocket関連関数 =====
def on_message(ws, message):
    root.after(0, chat_box.insert, tk.END, f"サーバー: {message}\n")
    root.after(0, chat_box.yview, tk.END)


def on_error(ws, error):
    print(f"WebSocketエラー: {error}")


def on_close(ws, close_status_code, close_msg):
    print("WebSocket接続が閉じました。")


def on_open(ws):
    print("WebSocket接続成功。")


def start_websocket():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()


# ===== チャット関連機能 =====
def send_message():
    message = chat_entry.get()
    if message:
        ws.send(json.dumps({'message': message}))
        chat_box.insert(tk.END, f"クライアント: {message}\n")
        chat_box.yview(tk.END)
        chat_entry.delete(0, tk.END)


def chat_window():
    global chat_box, chat_entry, ws
    chat_win = Toplevel()
    chat_win.title("リアルタイムチャット")

    chat_box = Text(chat_win, height=15, width=50)
    chat_box.pack()

    chat_entry = Entry(chat_win, width=50)
    chat_entry.pack()

    send_button = Button(chat_win, text="送信", command=send_message)
    send_button.pack()

    Thread(target=start_websocket, daemon=True).start()


# ===== ツール実行用コードエディタ =====
class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Pythonコードエディター")

        # メニュー設定
        menu = tk.Menu(root)
        root.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="保存", command=self.save_file)
        file_menu.add_command(label="開く", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=root.quit)

        run_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="実行", menu=run_menu)
        run_menu.add_command(label="ローカルで実行", command=self.run_code_locally)
        run_menu.add_command(label="サーバーで実行", command=self.run_code_on_server)

        # テキストエリア
        self.text_area = ScrolledText(root, wrap=tk.WORD, font=("Courier", 12))
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # 実行結果エリア
        self.output_area = ScrolledText(root, wrap=tk.WORD, font=("Courier", 12), height=10, state=tk.DISABLED)
        self.output_area.pack(fill=tk.BOTH, expand=True)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get("1.0", tk.END))

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)

    def run_code_locally(self):
        code = self.text_area.get("1.0", tk.END)
        temp_file = "temp_code.py"
        with open(temp_file, "w") as file:
            file.write(code)

        result = subprocess.run(["python", temp_file], capture_output=True, text=True)
        os.remove(temp_file)
        self.display_output(result.stdout, result.stderr)

    def run_code_on_server(self):
        code = self.text_area.get("1.0", tk.END)
        files = {'file': ('temp_code.py', code)}
        try:
            response = requests.post(f"{SERVER_URL}/script_execute", files=files)
            if response.status_code == 200:
                result = response.json()
                self.display_output(result.get("log", ""), "サーバー実行成功")
            else:
                self.display_output("", f"サーバーエラー: {response.status_code}")
        except Exception as e:
            self.display_output("", f"接続エラー: {str(e)}")

    def display_output(self, stdout, stderr):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert("1.0", "標準出力:\n" + stdout)
        self.output_area.insert(tk.END, "\n標準エラー:\n" + stderr)
        self.output_area.config(state=tk.DISABLED)

# =====ツール表示機能 =====

def select_tool_and_params():
    tools = fetch_tool_list()
    if not tools:
        return
    
    tool_window = Toplevel()
    tool_window.title("ツール選択")

    tool_label = Label(tool_window, text="ツールを選んでください")
    tool_label.pack(pady=10)

    tool_var = tk.StringVar()
    tool_menu = tk.OptionMenu(tool_window, tool_var, *[tool['name'] for tool in tools])
    tool_menu.pack(pady=10)

    param_label = Label(tool_window, text="パラメータ:")
    param_label.pack(pady=10)

    param_entry = Entry(tool_window, width=50)
    param_entry.pack(pady=10)

    def execute_tool():
        selected_tool = tool_var.get()
        parameters = param_entry.get()
        messagebox.showinfo("実行", f"選択されたツール: {selected_tool}\nパラメータ: {parameters}")
        # サーバーにツールとパラメータを送信する、または他の処理を行うことができます。

    execute_button = Button(tool_window, text="実行", command=execute_tool)
    execute_button.pack(pady=10)


# ===== メインGUI =====
def main_gui():
    global root
    root = tk.Tk()
    root.title("ツール実行クライアント")

    Button(root, text="チャットを開く", command=chat_window).pack(pady=10)
    Button(root, text="コードエディタを開く", command=open_code_editor).pack(pady=10)
    Button(root, text="ツールリストを表示", command=select_tool_and_params).pack(pady=10)
    Button(root, text="ログを表示", command=display_logs).pack(pady=10)
    Button(root, text="終了", command=root.quit).pack(pady=10)
    root.mainloop()


def open_code_editor():
    editor_window = Toplevel()
    CodeEditor(editor_window)


# ===== アプリケーション起動 =====
if __name__ == "__main__":
    main_gui()
