from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.user.entities import User as UserEntity

class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserEntity]: # Changed to int
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def create(self, user_data: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def update(self, user_id: int, user_data: UserEntity) -> Optional[UserEntity]: # Changed to int
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool: # Changed to int
        pass
