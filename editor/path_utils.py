import json
import os
import shutil
import sys


def get_application_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_project_root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_directory():
    data_dir = os.path.join(get_project_root(), "local_storage")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_saves_directory():
    saves_dir = os.path.join(get_data_directory(), "saves")
    os.makedirs(saves_dir, exist_ok=True)
    return saves_dir


def get_exports_directory():
    exports_dir = os.path.join(get_data_directory(), "exports")
    os.makedirs(exports_dir, exist_ok=True)
    return exports_dir


def get_settings_path():
    data_dir = get_data_directory()
    settings_path = os.path.join(data_dir, "settings.json")
    if not os.path.exists(settings_path):
        default_settings = {
            "theme": "dark",
        }
        with open(settings_path, "w") as f:
            json.dump(default_settings, f)
    return settings_path


def get_recent_files_path():
    data_dir = get_data_directory()
    recent_files_path = os.path.join(data_dir, "recent_files.json")
    if not os.path.exists(recent_files_path):
        bundled_recent_files = os.path.join(
            get_application_path(), "editor", "recent_files.json"
        )
        if os.path.isfile(bundled_recent_files):
            shutil.copyfile(bundled_recent_files, recent_files_path)
        else:
            with open(recent_files_path, "w") as recent_files:
                json.dump([], recent_files)
    return recent_files_path