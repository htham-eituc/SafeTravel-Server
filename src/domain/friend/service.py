from sqlalchemy.orm import Session
from .repository import FriendRepository
from .schemas import FriendCreate

class FriendService:
    def __init__(self, friend_repository: FriendRepository):
        self.friend_repository = friend_repository

    def get_friend(self, db: Session, friend_id: int):
        return self.friend_repository.get_friend(db, friend_id)

    def get_friends_by_user_id(self, db: Session, user_id: int):
        return self.friend_repository.get_friends_by_user_id(db, user_id)

    def create_friend(self, db: Session, friend: FriendCreate):
        return self.friend_repository.create_friend(db, friend)

    def delete_friend(self, db: Session, friend_id: int):
        return self.friend_repository.delete_friend(db, friend_id)
