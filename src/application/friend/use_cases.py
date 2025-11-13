from sqlalchemy.orm import Session
from src.domain.friend.repository_interface import IFriendRepository
from src.application.friend.dto import FriendCreate
from src.domain.friend.entities import Friend as FriendEntity

class FriendUseCases:
    def __init__(self, friend_repository: IFriendRepository):
        self.friend_repository = friend_repository

    def get_friend(self, db: Session, friend_id: int) -> Optional[FriendEntity]:
        return self.friend_repository.get_friend(db, friend_id)

    def get_friends_by_user_id(self, db: Session, user_id: int) -> List[FriendEntity]:
        return self.friend_repository.get_friends_by_user_id(db, user_id)

    def create_friend(self, db: Session, friend_data: FriendCreate) -> FriendEntity:
        friend_entity = FriendEntity(user_id=friend_data.user_id, friend_user_id=friend_data.friend_user_id, status="pending") # Default status
        return self.friend_repository.create_friend(db, friend_entity)

    def delete_friend(self, db: Session, friend_id: int) -> Optional[FriendEntity]:
        return self.friend_repository.delete_friend(db, friend_id)
