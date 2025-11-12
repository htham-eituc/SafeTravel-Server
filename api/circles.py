from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas.circle import CircleCreate, CircleInDB as CircleSchema, CircleUpdate
from services.circle_service import CircleService
from repositories.circle_repository import CircleRepository
from repositories.circle_member_repository import CircleMemberRepository
from api.dependencies import get_current_user
from models.user import User

router = APIRouter(
    prefix="/circles",
    tags=["circles"],
    dependencies=[Depends(get_current_user)]
)

def get_circle_service(
    db: Session = Depends(get_db)
) -> CircleService:
    circle_repository = CircleRepository(db)
    circle_member_repository = CircleMemberRepository(db)
    return CircleService(circle_repository, circle_member_repository)

@router.post("/", response_model=CircleSchema, status_code=status.HTTP_201_CREATED)
def create_circle(
    circle: CircleCreate,
    current_user: User = Depends(get_current_user),
    circle_service: CircleService = Depends(get_circle_service)
):
    return circle_service.create_circle(circle, current_user.id)

@router.get("/", response_model=List[CircleSchema])
def get_circles(
    current_user: User = Depends(get_current_user),
    circle_service: CircleService = Depends(get_circle_service)
):
    return circle_service.get_circles_by_owner_id(current_user.id)

@router.get("/{circle_id}", response_model=CircleSchema)
def get_circle(
    circle_id: int,
    current_user: User = Depends(get_current_user),
    circle_service: CircleService = Depends(get_circle_service)
):
    db_circle = circle_service.get_circle(circle_id)
    if not db_circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    if db_circle.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this circle"
        )
    return db_circle

@router.put("/{circle_id}", response_model=CircleSchema)
def update_circle(
    circle_id: int,
    circle_update: CircleUpdate,
    current_user: User = Depends(get_current_user),
    circle_service: CircleService = Depends(get_circle_service)
):
    db_circle = circle_service.get_circle(circle_id)
    if not db_circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    if db_circle.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this circle"
        )
    return circle_service.update_circle(circle_id, circle_update)

@router.delete("/{circle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_circle(
    circle_id: int,
    current_user: User = Depends(get_current_user),
    circle_service: CircleService = Depends(get_circle_service)
):
    db_circle = circle_service.get_circle(circle_id)
    if not db_circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
    if db_circle.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this circle"
        )
    circle_service.delete_circle(circle_id)
    return {"message": "Circle deleted successfully"}
