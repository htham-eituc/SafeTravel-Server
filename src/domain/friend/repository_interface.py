from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from ..friend.entities import FriendRequest, Friendship
from ..user.entities import User as UserEntity

class IFriendRepository(ABC):
    @abstractmethod
    def send_friend_request(self, db: Session, sender_id: int, receiver_id: int) -> FriendRequest:
        pass

    @abstractmethod
    def get_friend_request(self, db: Session, request_id: int) -> Optional[FriendRequest]:
        pass

    @abstractmethod
    def get_pending_friend_requests(self, db: Session, user_id: int) -> List[FriendRequest]:
        pass

    @abstractmethod
    def accept_friend_request(self, db: Session, request_id: int) -> FriendRequest:
        pass

    @abstractmethod
    def reject_friend_request(self, db: Session, request_id: int) -> FriendRequest:
        pass

    @abstractmethod
    def create_friendship(self, db: Session, user_id: int, friend_id: int) -> Friendship:
        pass

    @abstractmethod
    def get_friendship(self, db: Session, user_id: int, friend_id: int) -> Optional[Friendship]:
        pass

    @abstractmethod
    def delete_friendship(self, db: Session, friendship_id: int) -> Optional[Friendship]:
        pass

    @abstractmethod
    def get_friends_by_user_id(self, db: Session, user_id: int) -> List[UserEntity]:
        pass

    @abstractmethod
    def get_user_by_username(self, db: Session, username: str) -> Optional[UserEntity]:
        pass
