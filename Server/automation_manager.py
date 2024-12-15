import subprocess
import os

COMMANDS_DIR = "./commands"

def execute_script(filename):
    script_path = os.path.join(COMMANDS_DIR, filename)
    if not os.path.exists(script_path):
        return {"error": f"{filename} が存在しません。"}
    try:
        result = subprocess.run(["bash", script_path], capture_output=True, text=True, check=True)
        return {"output": result.stdout, "error": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"output": e.stdout, "error": e.stderr}

def list_scripts():
    return [f for f in os.listdir(COMMANDS_DIR) if os.path.isfile(os.path.join(COMMANDS_DIR, f))]
