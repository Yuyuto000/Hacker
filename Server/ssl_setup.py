import subprocess

def setup_ssl():
    try:
        subprocess.run(["openssl", "req", "-new", "-x509", "-days", "365", 
                        "-nodes", "-out", "cert.pem", "-keyout", "key.pem", 
                        "-subj", "/CN=localhost"], check=True)
        print("SSL証明書を生成しました。")
    except Exception as e:
        print(f"SSLセットアップエラー: {e}")
