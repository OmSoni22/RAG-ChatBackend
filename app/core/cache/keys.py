from enum import Enum

class CacheKeys(str, Enum):
    """
    Centralized cache keys for the application.
    Using Enum for type safety and discovery.
    """
    USER_LIST = "users:list"
    
    # Example for dynamic keys
    # @staticmethod
    # def user_detail(user_id: int) -> str:
    #     return f"users:detail:{user_id}"
