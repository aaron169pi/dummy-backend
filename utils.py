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
        print("[INFO]", message)     # Issue: No structured logging
        self._write("INFO", message)

    def error(self, message: str):
        print("[ERROR]", message)
        self._write("ERROR", message)


def load_config(path: str):
    # Issue: No default fallback, crashes if file missing
    with open(path, "r") as f:
        raw = f.read()

    # Issue: No JSON validation / try-except
    data = json.loads(raw)

    # Potential issue: nested keys may be missing
    return data


def validate_age(age):
    # Issue: Unused helper function
    if not isinstance(age, int):
        raise ValueError("Age must be integer")

    if age < 0 or age > 150:
        raise ValueError("Age out of range")

    return True

