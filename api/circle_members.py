from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas.circle_member import CircleMemberCreate, CircleMemberInDB as CircleMemberSchema
from services.circle_member_service import CircleMemberService
from repositories.circle_member_repository import CircleMemberRepository
from api.dependencies import get_current_user
from models.user import User

router = APIRouter(
    prefix="/circle_members",
    tags=["circle_members"],
    dependencies=[Depends(get_current_user)]
)

def get_circle_member_service(db: Session = Depends(get_db)) -> CircleMemberService:
    repository = CircleMemberRepository(db)
    return CircleMemberService(repository)

@router.post("/", response_model=CircleMemberSchema, status_code=status.HTTP_201_CREATED)
def add_circle_member(
    circle_member: CircleMemberCreate,
    current_user: User = Depends(get_current_user),
    circle_member_service: CircleMemberService = Depends(get_circle_member_service)
):
    # You might want to add logic here to ensure the current_user has permission
    # to add members to the specified circle (e.g., they are the owner of the circle)
    return circle_member_service.create_circle_member(circle_member)

@router.get("/circle/{circle_id}", response_model=List[CircleMemberSchema])
def get_circle_members(
    circle_id: int,
    current_user: User = Depends(get_current_user),
    circle_member_service: CircleMemberService = Depends(get_circle_member_service)
):
    # You might want to add logic here to ensure the current_user has permission
    # to view members of the specified circle
    return circle_member_service.get_circle_members_by_circle(circle_id)

@router.delete("/{circle_member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_circle_member(
    circle_member_id: int,
    current_user: User = Depends(get_current_user),
    circle_member_service: CircleMemberService = Depends(get_circle_member_service)
):
    db_circle_member = circle_member_service.get_circle_member(circle_member_id)
    if not db_circle_member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle member not found")
    
    # You might want to add logic here to ensure the current_user has permission
    # to remove this member (e.g., they are the owner of the circle or the member themselves)
    
    circle_member_service.delete_circle_member(circle_member_id)
    return {"message": "Circle member deleted successfully"}
