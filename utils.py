python
import json
from datetime import datetime
from typing import Dict, Any

class Logger:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _write(self, level: str, message: str):
        """Write log entry with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
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
    """Load configuration with error handling and defaults"""
    default_config = {
        "debug_mode": False,
        "max_users": 1000,
        "timeout_seconds": 30,
        "discount_rate": 0.1,
        "age_threshold": 40
    }

    try:
        with open(path, "r") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"Config file '{path}' not found, using defaults")
        return default_config
        
    try:
        data = json.loads(raw)
        
        # Validate required fields
        if "discount_rate" not in data:
            raise ValueError("Missing required field 'discount_rate'")
            
        return {**default_config, **data}
    except json.JSONDecodeError:
        print(f"Failed to parse config file '{path}', using defaults")
        return default_config


def reload_config(path: str) -> Dict[str, Any]:
    """Reload configuration from file"""
    return load_config(path)


def filter_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Filter sensitive configuration values"""
    filtered = {}
    sensitive_keys = ["database_password", "secret_key"]
    
    for key, value in config.items():
        if key not in sensitive_keys:
            filtered[key] = value
            
    return filtered