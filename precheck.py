import os
import pathlib

import win32api
import win32con

import settings


def create_folders():
    """
    Create necessary folders if they don't exist and set the folders starting with '.' to hidden.

    Folders created:
    - .logs: saves log files
    - .cache: saves thumbnails frames as qoi files
    - .metadata: saves changes in window focus as tsv files
    - .settings: saves multiple setting profiles as yaml files
    - .thumbnails: saves thumbnails as webp animations
    - Records: saves the actual recordings as mkv files
    """
    # Create the HOME_DIR if it doesn't exist
    if not settings.HOME_DIR:
        user_dir = os.path.expanduser("~")
        homepath = pathlib.Path(user_dir) / "SempRecord"
        homepath.mkdir(exist_ok=True)
        settings.HOME_DIR = homepath

    HOME_DIR = settings.HOME_DIR
    HOME_DIR = pathlib.Path(HOME_DIR)
    HOME_DIR.mkdir(exist_ok=True)

    # Create the following folders if they don't exist
    for folder in [
        ".logs",
        ".cache",
        ".metadata",
        ".settings",
        ".thumbnails",
        "Records",
    ]:
        (HOME_DIR / folder).mkdir(exist_ok=True)

    # Set the folders starting with . to hidden
    for f in HOME_DIR.iterdir():
        if f.name.startswith("."):
            win32api.SetFileAttributes(str(f), win32con.FILE_ATTRIBUTE_HIDDEN)


def cleaning_out_my_closet():
    """clear out corrupst files by deleting any file less than 1MB from the Records folder"""
    MIN_SIZE = 1_000_000
    for file in (settings.HOME_DIR / "Records").iterdir():
        if file.stat().st_size < MIN_SIZE:
            file.unlink()
            print(f"Deleted {file.name}")


create_folders()
cleaning_out_my_closet()

try:
    settings.load()
except FileNotFoundError:
    print("No settings file found. Creating a new one.")
    settings.save()
