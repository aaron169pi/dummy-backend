python
import json
from datetime import datetime

class Logger:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _write(self, level: str, message: str):
        timestamp = datetime.now().isoformat()
        line = f"[{timestamp}] [{level}] {message}\n"
        with open(self.file_path, "a") as f:
            f.write(line)

    def info(self, message: str):
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [INFO] {message}") 
        self._write("INFO", message)

    def error(self, message: str):
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [ERROR] {message}")
        self._write("ERROR", message)


def load_config(path: str):
    default_config = {
        "discount_rate": 0.1,
        "age_threshold": 40,
        "debug_mode": False
    }

    try:
        with open(path, "r") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"Config file '{path}' not found. Using default configuration.")
        return default_config

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"Invalid JSON format in config file '{path}'. Using default configuration.")
        return default_config
    
    # Merge with defaults to ensure required fields
    merged_config = {**default_config, **data}
    return merged_config


def mask_sensitive_data(data: dict) -> dict:
    """Masks sensitive values in dictionary"""
    masked = {}
    for key, value in data.items():
        if key.endswith(("_password", "_secret", "_token")):
            masked[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked[key] = mask_sensitive_data(value)
        else:
            masked[key] = value
    return masked