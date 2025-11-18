from sqlalchemy.orm import Session
from src.domain.friend.repository_interface import IFriendRepository
from src.application.friend.dto import FriendRequestCreate, FriendRequestResponse, FriendshipResponse
from src.domain.friend.entities import FriendRequest as FriendRequestEntity, Friendship as FriendshipEntity
from src.infrastructure.friend.models import FriendRequest as FriendRequestModel
from src.domain.user.entities import User as UserEntity
from typing import List, Optional

class FriendUseCases:
    def __init__(self, friend_repository: IFriendRepository):
        self.friend_repository = friend_repository

    def send_friend_request(self, db: Session, sender_id: int, friend_request_data: FriendRequestCreate) -> FriendRequestResponse:
        receiver_username = friend_request_data.receiver_username
        receiver_user = self.friend_repository.get_user_by_username(db, receiver_username)

        if not receiver_user:
            raise ValueError("Receiver user not found.")
        if sender_id == receiver_user.id:
            raise ValueError("Cannot send friend request to yourself.")

        # Check if a pending request already exists
        existing_request = db.query(FriendRequestModel).filter(
            ((FriendRequestModel.sender_id == sender_id) & (FriendRequestModel.receiver_id == receiver_user.id)) |
            ((FriendRequestModel.sender_id == receiver_user.id) & (FriendRequestModel.receiver_id == sender_id)),
            FriendRequestModel.status == "pending"
        ).first()
        if existing_request:
            raise ValueError("A pending friend request already exists with this user.")

        # Check if they are already friends
        existing_friendship = self.friend_repository.get_friendship(db, sender_id, receiver_user.id)
        if existing_friendship:
            raise ValueError("You are already friends with this user.")

        friend_request_entity = self.friend_repository.send_friend_request(db, sender_id, receiver_user.id)
        return FriendRequestResponse.model_validate(friend_request_entity.__dict__)

    def get_pending_friend_requests(self, db: Session, user_id: int) -> List[FriendRequestResponse]:
        pending_requests = self.friend_repository.get_pending_friend_requests(db, user_id)
        return [FriendRequestResponse.model_validate(fr.__dict__) for fr in pending_requests]

    def accept_friend_request(self, db: Session, request_id: int, user_id: int) -> FriendshipResponse:
        friend_request = self.friend_repository.get_friend_request(db, request_id)

        if not friend_request:
            raise ValueError("Friend request not found.")
        if friend_request.receiver_id != user_id:
            raise ValueError("You are not authorized to accept this request.")
        if friend_request.status != "pending":
            raise ValueError("Friend request is not pending.")

        accepted_request = self.friend_repository.accept_friend_request(db, request_id)
        friendship = self.friend_repository.create_friendship(db, accepted_request.sender_id, accepted_request.receiver_id)
        return FriendshipResponse.model_validate(friendship.__dict__)

    def reject_friend_request(self, db: Session, request_id: int, user_id: int) -> FriendRequestResponse:
        friend_request = self.friend_repository.get_friend_request(db, request_id)

        if not friend_request:
            raise ValueError("Friend request not found.")
        if friend_request.receiver_id != user_id:
            raise ValueError("You are not authorized to reject this request.")
        if friend_request.status != "pending":
            raise ValueError("Friend request is not pending.")

        rejected_request = self.friend_repository.reject_friend_request(db, request_id)
        return FriendRequestResponse.model_validate(rejected_request.__dict__)

    def get_friends_by_user_id(self, db: Session, user_id: int) -> List[UserEntity]:
        return self.friend_repository.get_friends_by_user_id(db, user_id)
