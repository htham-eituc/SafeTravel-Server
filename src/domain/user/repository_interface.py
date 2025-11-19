from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.user.entities import User as UserEntity

class IUserRepository(ABC):
    @abstractmethod
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def get_user_by_username(self, db: Session, username: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def create_user(self, db: Session, user_data: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def update_user(self, db: Session, user_id: int, user_data: UserEntity) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def delete_user(self, db: Session, user_id: int) -> bool:
        pass
