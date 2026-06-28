import os
import sys

def get_application_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_data_directory():
    if getattr(sys, 'frozen', False):
        data_dir = os.path.join(os.path.expanduser("~"), ".bunnynode")
    else:
        data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
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
    return os.path.join(data_dir, "your_settings.json")