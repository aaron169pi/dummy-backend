python
from utils import Logger

class UserService:
    def __init__(self, config, logger: Logger):
        self.config = config
        self.logger = logger
        self.users = self.load_users()
        self.next_id = len(self.users) + 1
        
    def load_users(self):
        """Load users from persistent storage"""
        try:
            with open("users.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load users: {str(e)}")
            return {}

    def save_users(self):
        """Save users to persistent storage"""
        try:
            with open("users.json", "w") as f:
                json.dump(self.users, f)
        except Exception as e:
            self.logger.error(f"Failed to save users: {str(e)}")

    def list_users(self):
        return list(self.users.values())

    def get_user(self, user_id: int):
        return self.users.get(str(user_id))

    def create_user(self, name: str, age: int):
        # Validate age before creating user
        if not self.validate_age(age):
            raise ValueError("Invalid age value")

        user = {
            "id": self.next_id,
            "name": name,
            "age": age
        }
        
        self.users[str(self.next_id)] = user
        self.save_users()  # Save changes immediately
        self.logger.info(f"Created user {user}")
        self.next_id += 1
        return user

    def calculate_discount(self, user_id: int):
        try:
            user = self.get_user(user_id)
            if not user:
                raise ValueError("User does not exist")

            # Get config values with fallbacks
            rate = self.config.get("discount_rate", 0.1)
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
                return age * rate
            else:
                return (threshold_age - age) * rate

        except ValueError as ve:
            self.logger.error(f"Validation error: {ve}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error calculating discount: {e}")
            raise

    def validate_age(self, age):
        """Validate age input value"""
        try:
            age = int(age)
            if 0 <= age <= 150:
                return True
            return False
        except (ValueError, TypeError):
            return False