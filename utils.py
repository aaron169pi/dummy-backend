import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

DEFAULT_CONFIG = {
    "discount_rate": 0.1,
    "age_threshold": 40,
    "database": {
        "host": "localhost",
        "port": 5432
    }
}

class Logger:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_log_file_exists()

    def _ensure_log_file_exists(self):
        Path(self.file_path).touch(exist_ok=True)

    def _write(self, level: str, message: str):
        timestamp = datetime.now().isoformat()
        line = f"[{timestamp}] [{level}] {message}\n"
        with open(self.file_path, "a") as f:
            f.write(line)

    def info(self, message: str):
        self._write("INFO", message)

    def error(self, message: str):
        self._write("ERROR", message)


def load_config(path: str = "settings.json") -> Dict[str, Any]:
    """Load configuration with error handling and default fallback"""
    try:
        config_path = Path(path)
        
        if not config_path.exists():
            print(f"Config file not found at {path}. Using defaults.")
            return DEFAULT_CONFIG.copy()

        with open(path, "r") as f:
            raw = f.read()

        try:
            data = json.loads(raw)
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(data)
            return merged_config
        except json.JSONDecodeError as e:
            print(f"Failed to parse config file: {e}")
            return DEFAULT_CONFIG.copy()

    except Exception as e:
        print(f"Unexpected error loading config: {e}")
        return DEFAULT_CONFIG.copy()


def reload_config(path: str = "settings.json") -> Dict[str, Any]:
    """Reload configuration from disk"""
    return load_config(path)