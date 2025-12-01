python
from typing import Dict, List, Optional
from pydantic import BaseModel, ValidationError
from utils import Logger, load_config

class UserSchema(BaseModel):
    id: int
    name: str
    age: int

class UserService:
    def __init__(self, config, logger: Logger):
        self.config = config
        self.logger = logger
        self.users_file = "users.json"
        
        # Initialize with persisted users or empty state
        self.users = self.load_users()
        self.next_id = max(self.users.keys(), default=0) + 1

    def load_users(self) -> Dict[int, Dict]:
        """Load users from JSON file"""
        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load users: {str(e)}")
            return {}

    def save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.users_file, "w") as f:
                json.dump(self.users, f)
        except Exception as e:
            self.logger.error(f"Failed to save users: {str(e)}")

    def list_users(self) -> List[Dict]:
        return list(self.users.values())

    def get_user(self, user_id: int) -> Optional[Dict]:
        return self.users.get(user_id)

    def create_user(self, name: str, age: int) -> Dict:
        # Validate age input
        try:
            UserSchema(age=age).dict()
        except ValidationError as e:
            raise ValueError(f"Invalid age format: {str(e)}")

        user = {
            "id": self.next_id,
            "name": name,
            "age": age
        }
        
        self.users[self.next_id] = user
        self.save_users()  # Persist immediately
        self.logger.info(f"Created user {user}")
        self.next_id += 1
        return user

    def calculate_discount(self, user_id: int) -> float:
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User does not exist")

        rate = self.config.get("discount_rate", 0)
        threshold_age = self.config.get("age_threshold", 40)

        if rate <= 0:
            raise ValueError("Invalid discount_rate must be greater than 0")

        age = user.get("age")
        if age is None:
            raise ValueError("User has no age")

        self.logger.info(
            f"Calculating discount for user={user_id}, age={age}, rate={rate}"
        )

        if age > threshold_age:
            return round(age * rate, 2)
        else:
            return round((threshold_age - age) * rate, 2)