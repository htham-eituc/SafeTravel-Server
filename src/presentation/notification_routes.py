from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.application.notification.dto import NotificationCreate, NotificationUpdate, NotificationInDB
from src.application.notification.use_cases import NotificationUseCases
from src.infrastructure.notification.repository_impl import NotificationRepository
from src.infrastructure.database.sql.database import get_db
from src.application.dependencies import get_notification_use_cases

router = APIRouter()

@router.post("/notifications", response_model=NotificationInDB, status_code=status.HTTP_201_CREATED)
def create_notification_route(
    notification_data: NotificationCreate,
    notification_use_cases: NotificationUseCases = Depends(get_notification_use_cases),
    db: Session = Depends(get_db)
):
    notification = notification_use_cases.create_notification(db, notification_data)
    return NotificationInDB.model_validate(notification)

@router.get("/notifications/{notification_id}", response_model=NotificationInDB)
def get_notification_route(
    notification_id: int,
    notification_use_cases: NotificationUseCases = Depends(get_notification_use_cases),
    db: Session = Depends(get_db)
):
    notification = notification_use_cases.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return NotificationInDB.model_validate(notification)

from src.application.dependencies import get_current_user
from src.domain.user.entities import User as UserEntity

# ... (rest of the file)

@router.get("/notifications", response_model=List[NotificationInDB])
def get_notifications_by_user_route(
    current_user: UserEntity = Depends(get_current_user),
    notification_use_cases: NotificationUseCases = Depends(get_notification_use_cases),
    db: Session = Depends(get_db)
):
    notifications = notification_use_cases.get_notifications_by_user(db, current_user.id)
    return [NotificationInDB.model_validate(n) for n in notifications]

@router.put("/notifications/{notification_id}", response_model=NotificationInDB)
def update_notification_route(
    notification_id: int,
    notification_update: NotificationUpdate,
    notification_use_cases: NotificationUseCases = Depends(get_notification_use_cases),
    db: Session = Depends(get_db)
):
    notification = notification_use_cases.update_notification(db, notification_id, notification_update)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return NotificationInDB.model_validate(notification)

@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification_route(
    notification_id: int,
    notification_use_cases: NotificationUseCases = Depends(get_notification_use_cases),
    db: Session = Depends(get_db)
):
    if not notification_use_cases.delete_notification(db, notification_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return
