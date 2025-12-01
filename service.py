from utils import Logger

class UserService:
    def __init__(self, config, logger: Logger):
        self.config = config
        self.logger = logger
        self.users = {}         # Issue: Not persistent
        self.next_id = 1        # Issue: Resets on every restart

    def list_users(self):
        return list(self.users.values())

    def get_user(self, user_id: int):
        return self.users.get(user_id)

    def create_user(self, name: str, age: int):
        # Issue: age might be None or string
        user = {
            "id": self.next_id,
            "name": name,
            "age": age
        }
        self.users[self.next_id] = user
        self.logger.info(f"Created user {user}")
        self.next_id += 1
        return user

    def calculate_discount(self, user_id: int):
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User does not exist")

        rate = self.config.get("discount_rate")   # Issue: might be None
        threshold_age = self.config.get("age_threshold", 40)

        if rate == 0:
            # Issue: Zero division scenario not fully prevented
            raise ValueError("Invalid discount_rate=0")

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

    def delete_user(self, user_id: int):
        # Issue: never used anywhere
        if user_id in self.users:
            self.logger.info(f"Deleted user {user_id}")
            del self.users[user_id]

