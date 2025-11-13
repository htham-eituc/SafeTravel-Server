from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from ..friend.entities import Friend as FriendEntity # Use alias to avoid conflict with ORM model

class IFriendRepository(ABC):
    @abstractmethod
    def get_friend(self, db: Session, friend_id: int) -> Optional[FriendEntity]:
        pass

    @abstractmethod
    def get_friends_by_user_id(self, db: Session, user_id: int) -> List[FriendEntity]:
        pass

    @abstractmethod
    def create_friend(self, db: Session, friend_data: FriendEntity) -> FriendEntity:
        pass

    @abstractmethod
    def delete_friend(self, db: Session, friend_id: int) -> Optional[FriendEntity]:
        pass
