from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated
from sqlalchemy.orm import Session
from src.application.dependencies import (
    get_current_user,
    get_db_session,
    get_circle_use_cases
)
from src.application.circle.dto import CircleCreate, CircleUpdate, CircleInDB, CircleMemberCreate, CircleMemberInDB
from src.application.circle.use_cases import CircleUseCases
from src.domain.user.entities import User as UserEntity
from src.application.user.dto import UserDTO

router = APIRouter()

@router.post("/circles", response_model=CircleInDB, status_code=status.HTTP_201_CREATED)
async def create_circle(
    circle_data: CircleCreate,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    circle_use_cases: CircleUseCases = Depends(get_circle_use_cases)
):
    """
    Create a new circle.
    The authenticated user will be set as the owner and automatically added as a member with the role "owner".
    Any existing active circles for the user will be set to "inactive".
    """
    try:
        new_circle = circle_use_cases.create_circle(db, circle_data, current_user.id)
        return new_circle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/circles", response_model=List[CircleInDB])
async def get_my_circles(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    circle_use_cases: CircleUseCases = Depends(get_circle_use_cases)
):
    """
    Get all circles owned by the current authenticated user.
    """
    try:
        circles = circle_use_cases.get_circles_by_owner(db, current_user.id)
        return circles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/circles/{circle_id}", response_model=CircleInDB)
async def get_specific_circle(
    circle_id: int,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    circle_use_cases: CircleUseCases = Depends(get_circle_use_cases)
):
    """
    Get details of a specific circle.
    Only the owner can view the circle.
    """
    circle = circle_use_cases.get_circle(db, circle_id)
    if not circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    if circle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this circle")
    return circle

@router.put("/circles/{circle_id}", response_model=CircleInDB)
async def update_circle(
    circle_id: int,
    circle_update: CircleUpdate,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    circle_use_cases: CircleUseCases = Depends(get_circle_use_cases)
):
    """
    Update an existing circle.
    Only the owner can update the circle.
    """
    existing_circle = circle_use_cases.get_circle(db, circle_id)
    if not existing_circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    if existing_circle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this circle")
    
    updated_circle = circle_use_cases.update_circle(db, circle_id, circle_update)
    if not updated_circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found after update attempt")
    return updated_circle

@router.delete("/circles/{circle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_circle(
    circle_id: int,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    circle_use_cases: CircleUseCases = Depends(get_circle_use_cases)
):
    """
    Delete a circle.
    Only the owner can delete the circle.
    """
    existing_circle = circle_use_cases.get_circle(db, circle_id)
    if not existing_circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    if existing_circle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this circle")
    
    if not circle_use_cases.delete_circle(db, circle_id):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete circle")

@router.post("/circles/{circle_id}/members", response_model=CircleMemberInDB, status_code=status.HTTP_201_CREATED)
async def add_member_to_circle(
    circle_id: int,
    member_data: CircleMemberCreate,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    circle_use_cases: CircleUseCases = Depends(get_circle_use_cases)
):
    """
    Add a member to a specific circle.
    Only the owner can add members.
    """
    existing_circle = circle_use_cases.get_circle(db, circle_id)
    if not existing_circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    if existing_circle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add members to this circle")
    
    try:
        new_member = circle_use_cases.add_member_to_circle(db, circle_id, member_data.user_id, member_data.role)
        return new_member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/circles/{circle_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_circle(
    circle_id: int,
    user_id: int,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    circle_use_cases: CircleUseCases = Depends(get_circle_use_cases)
):
    """
    Remove a member from a specific circle.
    Only the owner can remove members.
    """
    existing_circle = circle_use_cases.get_circle(db, circle_id)
    if not existing_circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    if existing_circle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to remove members from this circle")
    
    if not circle_use_cases.remove_member_from_circle(db, circle_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found in circle or could not be removed")

@router.get("/circles/{circle_id}/members", response_model=List[UserDTO])
async def get_circle_members(
    circle_id: int,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    circle_use_cases: CircleUseCases = Depends(get_circle_use_cases)
):
    """
    Get all members of a specific circle.
    Only the owner or a member of the circle can view the members.
    """
    existing_circle = circle_use_cases.get_circle(db, circle_id)
    if not existing_circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    
    # Check if current user is owner or a member
    is_owner = existing_circle.owner_id == current_user.id
    is_member = circle_use_cases.is_user_in_circle(db, circle_id, current_user.id)
    
    if not (is_owner or is_member):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view members of this circle")
    
    members = circle_use_cases.get_circle_members(db, circle_id)
    return [UserDTO.from_orm(member) for member in members]
