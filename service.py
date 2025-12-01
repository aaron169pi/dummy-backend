python
from typing import Dict, Any, Optional
from pathlib import Path
import json
from utils import Logger

class UserService:
    def __init__(self, config, logger: Logger):
        self.config = config
        self.logger = logger
        self.user_file = Path("users.json")
        
        # Initialize users from file
        self.users = self._load_users_from_file()
        self.next_id = self._get_next_available_id()
        
        # Register shutdown handler for saving
        import atexit
        atexit.register(self._save_users_to_file)

    def _load_users_from_file(self) -> Dict[int, Dict[str, Any]]:
        """Load users from JSON file"""
        try:
            if self.user_file.exists():
                with open(self.user_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load users: {e}")
            return {}

    def _save_users_to_file(self) -> None:
        """Save users to JSON file"""
        try:
            with open(self.user_file, "w") as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save users: {e}")

    def _get_next_available_id(self) -> int:
        """Get next available user ID"""
        if not self.users:
            return 1
        return max(self.users.keys()) + 1

    def list_users(self):
        return list(self.users.values())

    def get_user(self, user_id: int):
        return self.users.get(user_id)

    def create_user(self, name: str, age: int):
        if not isinstance(age, int) or age < 0 or age > 150:
            raise ValueError("Invalid age value")
            
        user = {
            "id": self.next_id,
            "name": name,
            "age": age
        }
        self.users[self.next_id] = user
        self.logger.info(f"Created user {user}")
        self._save_users_to_file()
        self.next_id = self._get_next_available_id()
        return user

    def calculate_discount(self, user_id: int):
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User does not exist")

        rate = self.config.get("discount_rate")
        if rate <= 0:
            raise ValueError("Invalid discount_rate (must be positive)")

        threshold_age = self.config.get("age_threshold", 40)
        age = user["age"]

        self.logger.info(
            f"Calculating discount for user={user_id}, age={age}, rate={rate}"
        )

        if age > threshold_age:
            return round(age * rate, 2)
        else:
            return round((threshold_age - age) * rate, 2)

    def delete_user(self, user_id: int):
        if user_id in self.users:
            deleted_user = self.users.pop(user_id)
            self.logger.info(f"Deleted user {deleted_user['name']}")
            self._save_users_to_file()
            return {"success": True}
        return {"success": False, "error": "User not found"}