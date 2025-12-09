from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from src.application.user.dto import UserDTO
from src.application.dependencies import get_db_session, provide_user_repository, get_current_user
from src.domain.user.repository_interface import IUserRepository
from src.domain.user.entities import User as UserEntity

router = APIRouter()

@router.get("/users/{user_id}", response_model=UserDTO)
async def get_user_by_id(
    user_id: int,
    current_user: Annotated[UserEntity, Depends(get_current_user)], # Ensure user is authenticated
    db: Session = Depends(get_db_session),
    user_repo: IUserRepository = Depends(provide_user_repository)
):
    """
    Get user details by ID.
    """
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserDTO.from_orm(user)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: Annotated[UserEntity, Depends(get_current_user)], # Ensure user is authenticated
    db: Session = Depends(get_db_session),
    user_repo: IUserRepository = Depends(provide_user_repository)
):
    """
    Delete a user by ID. Only the user themselves can delete their account.
    """
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
    
    if not user_repo.delete_user(db, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or could not be deleted")
