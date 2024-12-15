import os

def monitor_logs(log_dir):
    try:
        logs = {}
        for file_name in os.listdir(log_dir):
            with open(os.path.join(log_dir, file_name), "r") as f:
                logs[file_name] = f.readlines()
        return logs
    except Exception as e:
        print(f"ログ監視エラー: {e}")
        return {}
