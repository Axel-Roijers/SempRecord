import yaml
from pathlib import Path
from datetime import datetime
# Defaults must be upper case----------------------
RUN_ON_BOOT: bool = False
FRAME_RATE: int = 30
THUMBNAIL_RESOLUTION_REDUCTION: int = 5
THUMBNAIL_SECONDS_INTERVAL: int = 100  # in seconds
CHANGE_THRESHOLD = 2500  # sub-pixels
USE_AUTOTRIGGER = False
QUALITY = 32
#GENERATED-VARIABLES--------------------------------
HOME_DIR: Path = Path("D:/Videos") / "SempRecord"

try:
    user_dir_path = HOME_DIR / ".settings" / "recording_dir.txt"
    if user_dir_path.exists():
        with open(user_dir_path, "r") as f:
            chosen_path = f.read().strip()
        HOME_DIR = Path(chosen_path)
except:
    pass

def as_dict():
    settings = {}
    for k, v in globals().items():
        if k.isupper():
            settings[k] = v
    return settings


def save():
    settings = as_dict()
    settings["HOME_DIR"] = str(HOME_DIR)
    path = HOME_DIR / ".settings" / "settings.yaml"
    with open(path, "w") as f:
        yaml.dump(settings, f)
    

def load():
    global HOME_DIR
    path = HOME_DIR / ".settings" / "settings.yaml"
    with open(path, "r") as f:
        settings = yaml.safe_load(f.read())
        if not settings:
            return
        for k, v in settings.items():
            if k in globals():
                globals()[k] = v
            else:
                print(f"Unrecognized setting: {k}")
        HOME_DIR = Path(settings.get("HOME_DIR", HOME_DIR))
