import json
import os
from datetime import datetime


def save_dict_to_json(dict_var: dict, filename: str):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dict_var, f, ensure_ascii=False, indent=4)

def load_dict_from_json(filename: str):
    with open(filename, 'r', encoding="utf-8") as f:
        dict_var = json.load(f)
    return  dict_var

def save_file(dict_var: dict, dir_path: str, ext: str ="json"):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(dir_path, f"{timestamp}.{ext}")
    save_dict_to_json(dict_var, filename)

def load_file(dir_path: str, ext: str ="json"):
    files = [os.path.join(dir_path, f) for f in os.listdir(dir_path)]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return load_dict_from_json(latest_file)