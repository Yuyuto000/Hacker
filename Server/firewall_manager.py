import subprocess

def configure_firewall(rules):
    try:
        subprocess.run(["iptables", "-F"], check=True)  # 現在のルールをクリア
        for rule in rules:
            subprocess.run(["iptables"] + rule, check=True)
        print("ファイアウォール設定を適用しました。")
    except Exception as e:
        print(f"ファイアウォール設定エラー: {e}")
