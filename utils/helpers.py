import json
import os

def load_config():
    """Loads settings from config.json file"""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_path, 'config.json')

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {config_path} not found!")
        return None

def get_project_root():
    """Returns the absolute path to the project's root folder."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
