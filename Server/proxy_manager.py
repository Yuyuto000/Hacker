import subprocess

def configure_proxy(config):
    try:
        with open("/etc/squid/squid.conf", "w") as f:
            f.write(config)
        print("プロキシ設定を更新しました。")
    except Exception as e:
        print(f"プロキシ設定エラー: {e}")

def restart_proxy(config):
    try:
        configure_proxy(config)
        subprocess.run(["systemctl", "restart", "squid"], check=True)
        print("プロキシを再起動しました。")
    except Exception as e:
        print(f"プロキシ再起動エラー: {e}")
