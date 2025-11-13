from sqlalchemy.orm import Session
from src.infrastructure.friend.models import Friend
from src.domain.friend.repository_interface import IFriendRepository
from src.domain.friend.entities import Friend as FriendEntity
from src.application.friend.dto import FriendCreate # Assuming FriendCreate is a DTO

class FriendRepository(IFriendRepository):
    def get_friend(self, db: Session, friend_id: int) -> Optional[FriendEntity]:
        db_friend = db.query(Friend).filter(Friend.id == friend_id).first()
        if db_friend:
            return FriendEntity.model_validate(db_friend.__dict__)
        return None

    def get_friends_by_user_id(self, db: Session, user_id: int) -> List[FriendEntity]:
        db_friends = db.query(Friend).filter(Friend.user_id == user_id).all()
        return [FriendEntity.model_validate(f.__dict__) for f in db_friends]

    def create_friend(self, db: Session, friend_data: FriendEntity) -> FriendEntity:
        db_friend = Friend(user_id=friend_data.user_id, friend_user_id=friend_data.friend_user_id, status=friend_data.status)
        db.add(db_friend)
        db.commit()
        db.refresh(db_friend)
        return FriendEntity.model_validate(db_friend.__dict__)

    def delete_friend(self, db: Session, friend_id: int) -> Optional[FriendEntity]:
        db_friend = db.query(Friend).filter(Friend.id == friend_id).first()
        if db_friend:
            db.delete(db_friend)
            db.commit()
            return FriendEntity.model_validate(db_friend.__dict__)
        return None
