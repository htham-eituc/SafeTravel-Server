from sqlalchemy.orm import Session
from .friend import Friend
from .friend_schema import FriendCreate

class FriendRepository:
    def get_friend(self, db: Session, friend_id: int):
        return db.query(Friend).filter(Friend.id == friend_id).first()

    def get_friends_by_user_id(self, db: Session, user_id: int):
        return db.query(Friend).filter(Friend.user_id == user_id).all()

    def create_friend(self, db: Session, friend: FriendCreate):
        db_friend = Friend(user_id=friend.user_id, friend_id=friend.friend_id)
        db.add(db_friend)
        db.commit()
        db.refresh(db_friend)
        return db_friend

    def delete_friend(self, db: Session, friend_id: int):
        db_friend = db.query(Friend).filter(Friend.id == friend_id).first()
        if db_friend:
            db.delete(db_friend)
            db.commit()
        return db_friend
