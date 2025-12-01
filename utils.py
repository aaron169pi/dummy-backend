python
import json
from datetime import datetime
from typing import Any, Dict, NamedTuple, Optional, Union

class LogRecord(NamedTuple):
    """Named tuple for structured logging"""
    timestamp: str
    level: str
    source: str
    message: str

class Logger:
    """Improved structured logger with typing"""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _write(self, record: LogRecord) -> None:
        """Write formatted log record to file"""
        with open(self.file_path, "a") as f:
            f.write(f"{record.timestamp} [{record.level}] "
                    f"[{record.source}] {record.message}\n")

    def info(self, message: str, source: str = "APP") -> None:
        """Log informational message"""
        record = LogRecord(
            timestamp=datetime.now().isoformat(),
            level="INFO",
            source=source,
            message=message
        )
        self._write(record)

    def error(self, message: str, source: str = "APP") -> None:
        """Log error message"""
        record = LogRecord(
            timestamp=datetime.now().isoformat(),
            level="ERROR", 
            source=source,
            message=message
        )
        self._write(record)


def load_config(path: str) -> Dict[str, Any]:
    """Load config with error handling and defaults"""
    default_settings = {
        "debug_mode": False,
        "max_connections": 100,
        "timeout": 30,
        "age_threshold": 40,
        "discount_rate": 0.1
    }

    try:
        with open(path, "r") as f:
            raw = f.read()
    except FileNotFoundError:
        return default_settings
        
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return default_settings
        
    # Merge loaded config with defaults
    merged_config = default_settings.copy()
    merged_config.update(data)
    
    return merged_config