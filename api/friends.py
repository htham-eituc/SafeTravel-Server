from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas.friend import FriendCreate, Friend as FriendSchema
from services.friend_service import FriendService
from repositories.friend_repository import FriendRepository
from api.dependencies import get_current_user
from models.user import User

router = APIRouter(
    prefix="/friends",
    tags=["friends"],
    dependencies=[Depends(get_current_user)]
)

def get_friend_service(db: Session = Depends(get_db)) -> FriendService:
    repository = FriendRepository()
    return FriendService(repository)

@router.post("/", response_model=FriendSchema, status_code=status.HTTP_201_CREATED)
def create_friend(
    friend: FriendCreate,
    current_user: User = Depends(get_current_user),
    friend_service: FriendService = Depends(get_friend_service)
):
    if current_user.id != friend.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create friends for other users"
        )
    return friend_service.create_friend(friend_service.friend_repository.db, friend)

@router.get("/", response_model=List[FriendSchema])
def get_friends(
    current_user: User = Depends(get_current_user),
    friend_service: FriendService = Depends(get_friend_service)
):
    return friend_service.get_friends_by_user_id(friend_service.friend_repository.db, current_user.id)

@router.delete("/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_friend(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    friend_service: FriendService = Depends(get_friend_service)
):
    db_friend = friend_service.get_friend(friend_service.friend_repository.db, friend_id)
    if not db_friend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend not found")
    if db_friend.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this friend"
        )
    friend_service.delete_friend(friend_service.friend_repository.db, friend_id)
    return {"message": "Friend deleted successfully"}
