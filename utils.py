import json
from datetime import datetime
from typing import Dict, Any

class Logger:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _write(self, level: str, message: str):
        """Write log message with timestamp to file"""
        timestamp = datetime.now().isoformat()
        line = f"[{timestamp}] [{level}] {message}\n"
        with open(self.file_path, "a") as f:
            f.write(line)

    def info(self, message: str):
        """Log informational message"""
        self._write("INFO", message)

    def error(self, message: str):
        """Log error message"""
        self._write("ERROR", message)


def load_config(path: str) -> Dict[str, Any]:
    """Load configuration from file with error handling and defaults"""
    default_config = {
        "discount_rate": 0.1,
        "age_threshold": 40,
        "debug_mode": False
    }

    try:
        with open(path, "r") as f:
            try:
                data = json.load(f)
                # Merge with defaults, allowing defaults to be overridden
                merged_config = {**default_config, **data}
                return merged_config
            except json.JSONDecodeError:
                return default_config
    except FileNotFoundError:
        return default_config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return default_config