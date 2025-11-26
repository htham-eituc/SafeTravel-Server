from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.application.friend.dto import FriendRequestCreate, FriendRequestResponse, FriendshipResponse
from src.application.friend.use_cases import FriendUseCases
from src.application.dependencies import get_db, get_current_user, get_friend_use_cases
from src.domain.user.entities import User as UserEntity

router = APIRouter()

@router.post("/friend-requests", response_model=FriendRequestResponse, status_code=status.HTTP_201_CREATED)
def send_friend_request(
    friend_request_data: FriendRequestCreate,
    current_user: UserEntity = Depends(get_current_user),
    friend_use_cases: FriendUseCases = Depends(get_friend_use_cases),
    db: Session = Depends(get_db)
):
    try:
        return friend_use_cases.send_friend_request(db, current_user.id, friend_request_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/friend-requests/pending", response_model=List[FriendRequestResponse])
def get_pending_friend_requests(
    current_user: UserEntity = Depends(get_current_user),
    friend_use_cases: FriendUseCases = Depends(get_friend_use_cases),
    db: Session = Depends(get_db)
):
    return friend_use_cases.get_pending_friend_requests(db, current_user.id)

@router.post("/friend-requests/{request_id}/accept", response_model=FriendshipResponse)
def accept_friend_request(
    request_id: int,
    current_user: UserEntity = Depends(get_current_user),
    friend_use_cases: FriendUseCases = Depends(get_friend_use_cases),
    db: Session = Depends(get_db)
):
    try:
        return friend_use_cases.accept_friend_request(db, request_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/friend-requests/{request_id}/reject", response_model=FriendRequestResponse)
def reject_friend_request(
    request_id: int,
    current_user: UserEntity = Depends(get_current_user),
    friend_use_cases: FriendUseCases = Depends(get_friend_use_cases),
    db: Session = Depends(get_db)
):
    try:
        return friend_use_cases.reject_friend_request(db, request_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/friends", response_model=List[UserEntity])
def get_friends(
    current_user: UserEntity = Depends(get_current_user),
    friend_use_cases: FriendUseCases = Depends(get_friend_use_cases),
    db: Session = Depends(get_db)
):
    return friend_use_cases.get_friends_by_user_id(db, current_user.id)

@router.delete("/friends/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_friend(
    friend_id: int,
    current_user: UserEntity = Depends(get_current_user),
    friend_use_cases: FriendUseCases = Depends(get_friend_use_cases),
    db: Session = Depends(get_db)
):
    try:
        if not friend_use_cases.delete_friendship(db, current_user.id, friend_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
