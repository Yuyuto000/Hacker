import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import requests

# Pythonコードを書くためのエディターウィンドウ
class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Pythonコードエディター")

        # メニュー
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

        # エディター
        self.text_area = ScrolledText(root, wrap=tk.WORD, font=("Courier", 12))
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # 実行結果表示
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
        server_url = "http://localhost:5000/script_execute"  # サーバーのエンドポイント
        files = {'file': ('temp_code.py', code)}
        
        try:
            response = requests.post(server_url, files=files)
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

# クライアントメインメニュー
if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    root.mainloop()
