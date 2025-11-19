from sqlalchemy.orm import Session
from src.infrastructure.friend.models import FriendRequest, Friendship
from src.infrastructure.user.models import User as UserModel
from src.domain.friend.repository_interface import IFriendRepository
from src.domain.friend.entities import FriendRequest as FriendRequestEntity, Friendship as FriendshipEntity
from src.domain.user.entities import User as UserEntity

from typing import Optional, List
from datetime import datetime

class FriendRepository(IFriendRepository):
    def send_friend_request(self, db: Session, sender_id: int, receiver_id: int) -> FriendRequestEntity:
        db_friend_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id, status="pending")
        db.add(db_friend_request)
        db.commit()
        db.refresh(db_friend_request)
        return FriendRequestEntity.model_validate(db_friend_request.__dict__)

    def get_friend_request(self, db: Session, request_id: int) -> Optional[FriendRequestEntity]:
        db_friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
        if db_friend_request:
            return FriendRequestEntity.model_validate(db_friend_request.__dict__)
        return None

    def get_pending_friend_requests(self, db: Session, user_id: int) -> List[FriendRequestEntity]:
        db_friend_requests = db.query(FriendRequest).filter(
            FriendRequest.receiver_id == user_id,
            FriendRequest.status == "pending"
        ).all()
        return [FriendRequestEntity.model_validate(fr.__dict__) for fr in db_friend_requests]

    def accept_friend_request(self, db: Session, request_id: int) -> FriendRequestEntity:
        db_friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
        if db_friend_request:
            db_friend_request.status = "accepted"
            db_friend_request.updated_at = datetime.now()
            db.commit()
            db.refresh(db_friend_request)
            return FriendRequestEntity.model_validate(db_friend_request.__dict__)
        raise ValueError("Friend request not found")

    def reject_friend_request(self, db: Session, request_id: int) -> FriendRequestEntity:
        db_friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
        if db_friend_request:
            db_friend_request.status = "rejected"
            db_friend_request.updated_at = datetime.now()
            db.commit()
            db.refresh(db_friend_request)
            return FriendRequestEntity.model_validate(db_friend_request.__dict__)
        raise ValueError("Friend request not found")

    def create_friendship(self, db: Session, user_id: int, friend_id: int) -> FriendshipEntity:
        db_friendship = Friendship(user_id=user_id, friend_id=friend_id)
        db.add(db_friendship)
        db.commit()
        db.refresh(db_friendship)
        return FriendshipEntity.model_validate(db_friendship.__dict__)

    def get_friendship(self, db: Session, user_id: int, friend_id: int) -> Optional[FriendshipEntity]:
        db_friendship = db.query(Friendship).filter(
            ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
            ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id))
        ).first()
        if db_friendship:
            return FriendshipEntity.model_validate(db_friendship.__dict__)
        return None

    def delete_friendship(self, db: Session, friendship_id: int) -> Optional[FriendshipEntity]:
        db_friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()
        if db_friendship:
            db.delete(db_friendship)
            db.commit()
            return FriendshipEntity.model_validate(db_friendship.__dict__)
        return None

    def get_friends_by_user_id(self, db: Session, user_id: int) -> List[UserEntity]:
        friends_as_user = db.query(UserModel).join(Friendship, UserModel.id == Friendship.friend_id).filter(Friendship.user_id == user_id).all()
        friends_as_friend = db.query(UserModel).join(Friendship, UserModel.id == Friendship.user_id).filter(Friendship.friend_id == user_id).all()
        
        all_friends = friends_as_user + friends_as_friend
        unique_friends = {friend.id: friend for friend in all_friends}.values()
        
        return [UserEntity.model_validate(f.__dict__) for f in unique_friends]

    def get_user_by_username(self, db: Session, username: str) -> Optional[UserEntity]:
        db_user = db.query(UserModel).filter(UserModel.username == username).first()
        if db_user:
            return UserEntity.model_validate(db_user.__dict__)
        return None
