import subprocess

def configure_vpn(config):
    try:
        with open("/etc/wireguard/wg0.conf", "w") as f:
            f.write(config)
        print("VPN設定を更新しました。")
    except Exception as e:
        print(f"VPN設定エラー: {e}")

def restart_vpn(config):
    try:
        configure_vpn(config)
        subprocess.run(["systemctl", "restart", "wg-quick@wg0"], check=True)
        print("VPNを再起動しました。")
    except Exception as e:
        print(f"VPN再起動エラー: {e}")
