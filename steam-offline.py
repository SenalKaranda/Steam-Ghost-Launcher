import sys
import re
import subprocess
from pathlib import Path
import json

def get_app_dir():
    if getattr(sys, 'frozen', False):
        # Running as a bundled exe
        return Path(sys.executable).parent
    else:
        # Running from source
        return Path(__file__).parent

def load_steam_path_from_config():
    config_path = get_app_dir() / "config.json"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                return Path(config["userdata"]), Path(config["steam"])
        except Exception as e:
            print(f"Failed to parse config.json: {e}")
    return None, None

def find_latest_localconfig(userdata_root):
    latest_file = None
    latest_mtime = 0

    for user_dir in userdata_root.iterdir():
        config_path = user_dir / "config" / "localconfig.vdf"
        if config_path.exists():
            mtime = config_path.stat().st_mtime
            if mtime > latest_mtime:
                latest_file = config_path
                latest_mtime = mtime

    return latest_file

def update_persona_state(path):
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()

    pattern = r'(\\"ePersonaState\\":)(\d+)'
    new_content, count = re.subn(pattern, r'\g<1>7', content, count=1)

    if count == 0:
        print("No ePersonaState entry found.")
        return False

    with open(path, 'w', encoding='utf-8') as file:
        file.write(new_content)

    print(f"Successfully updated ePersonaState to 7 in:\n{path}")
    return True

def launch_steam(steam_root):
    steam_exe = steam_root / "steam.exe"
    if steam_exe.exists():
        print("🚀 Launching Steam...")
        subprocess.Popen([str(steam_exe)], shell=True)
    else:
        print(f"steam.exe not found at expected location: {steam_exe}")

if __name__ == "__main__":
    userdata_root, steam_root = load_steam_path_from_config()
    if not userdata_root or not steam_root:
        print("Config file missing or invalid. Please reinstall.")
        sys.exit(1)

    config_file = find_latest_localconfig(userdata_root)
    if config_file:
        if update_persona_state(config_file):
            launch_steam(steam_root)
    else:
        print("No localconfig.vdf file found in any userdata folders.")
