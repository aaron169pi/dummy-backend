from typing import Dict, Any, TypeVar
from collections import defaultdict

ConfigType = TypeVar('ConfigType')

class UserService:
    """
    Service class for managing user operations and calculations
    
    Args:
        config: Configuration settings
        logger: Logging instance
    """
    def __init__(self, config: ConfigType, logger: Logger):
        self.config = config
        self.logger = logger
        self.users: Dict[int, Dict[str, Any]] = defaultdict(dict)  # Makes users persistent across calls
        self.next_id = 1
        
    def list_users(self) -> Dict[str, Any]:
        """List all registered users"""
        return {"users": list(self.users.values())}

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID"""
        return self.users.get(user_id)

    def create_user(self, name: str, age: int) -> Dict[str, Any]:
        """Create new user with validation"""
        if not name:
            raise ValueError("Name is required")
            
        if not isinstance(age, int) or age <= 0:
            raise ValueError("Age must be positive integer")

        user = {
            "id": self.next_id,
            "name": name,
            "age": age
        }
        
        self.users[self.next_id] = user
        self.logger.info(f"Created user {user}", extra={"operation": "create"})
        self.next_id += 1
        return user

    def calculate_discount(self, user_id: int) -> float:
        """Calculate user discount with enhanced validation"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User does not exist")

        rate = self.config.get("discount_rate")
        threshold_age = self.config.get("age_threshold", 40)

        if rate is None or rate <= 0:
            raise ValueError("Invalid or missing discount_rate configuration")

        age = user.get("age")
        if age is None or age <= 0:
            raise ValueError("User has invalid age")

        self.logger.info(
            f"Calculating discount for user={user_id}, age={age}, rate={rate}",
            extra={"operation": "calculate"}
        )

        if age > threshold_age:
            discount = age * rate
        else:
            discount = (threshold_age - age) * rate
            
        self.logger.info(f"Calculated discount amount: {discount}", 
                        extra={"operation": "result"})
        return discount

    def delete_user(self, user_id: int) -> None:
        """Delete user (currently unused)"""
        if user_id in self.users:
            self.logger.info(f"Deleted user {user_id}", extra={"operation": "delete"})
            del self.users[user_id]