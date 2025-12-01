from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError
from fastapi import HTTPException
from utils import Logger

class UserConfigModel(BaseModel):
    discount_rate: float = Field(..., gt=0, description="Discount calculation rate")
    age_threshold: int = Field(40, ge=0, description="Age threshold for discounts")

class UserModel(BaseModel):
    id: int = Field(..., description="Unique user ID")
    name: str = Field(..., min_length=1, description="User name")
    age: int = Field(..., gt=0, description="User age")

class UserService:
    def __init__(self, config, logger: Logger):
        self._validate_config(config)
        self._config = config
        self.logger = logger
        self._users = {}
        self._next_id = 1
        
        # Try loading saved users
        self._load_users_from_file()

    @property
    def config(self) -> Dict[str, Any]:
        """Get filtered view of configuration"""
        return {
            "discount_rate": self._config["discount_rate"],
            "age_threshold": self._config["age_threshold"]
        }

    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> None:
        """Validate required configuration format"""
        try:
            UserConfigModel(**config)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration format: {str(e)}")

    def _save_users_to_file(self) -> None:
        """Save current state to file"""
        try:
            with open("users.json", "w") as f:
                json.dump(self._users, f)
        except IOError as e:
            self.logger.error(f"Failed to save users: {str(e)}")

    def _load_users_from_file(self) -> None:
        """Load users from file"""
        try:
            with open("users.json", "r") as f:
                self._users = json.load(f)
                self._next_id = max(self._users.keys(), default=1) + 1
        except (IOError, json.JSONDecodeError):
            self.logger.warning("Failed to load users from file")

    def list_users(self) -> List[Dict[str, Any]]:
        """List all registered users"""
        return list(self._users.values())

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self._users.get(user_id)

    def create_user(self, name: str, age: int) -> Dict[str, Any]:
        """Create new user"""
        try:
            UserModel(name=name, age=age)
        except ValidationError as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid user data: {str(e)}"
            )
            
        user = {
            "id": self._next_id,
            "name": name,
            "age": age
        }
        
        self._users[self._next_id] = user
        self.logger.info(f"Created user {user}")
        self._next_id += 1
        self._save_users_to_file()
        return user

    def calculate_discount(self, user_id: int) -> float:
        """Calculate discount for user"""
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        rate = self.config["discount_rate"]
        threshold_age = self.config["age_threshold"]
        age = user["age"]

        if rate <= 0:
            raise HTTPException(
                status_code=400, 
                detail="Invalid discount rate configuration"
            )
            
        if age <= 0:
            raise HTTPException(
                status_code=400, 
                detail="Invalid user age"
            )

        self.logger.info(
            f"Calculating discount for user={user_id}, "
            f"age={age}, rate={rate}"
        )

        if age > threshold_age:
            discount = age * rate
        else:
            discount = (threshold_age - age) * rate
            
        return round(discount, 2)