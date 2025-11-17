from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional

class IPasswordHasher(ABC):
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass

    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        pass

class ITokenService(ABC):
    @abstractmethod
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[int]: # Returns user_id (int)
        pass
