from sqlalchemy.orm import Session
from src.infrastructure.notification.models import Notification
from src.domain.notification.repository_interface import INotificationRepository
from src.domain.notification.entities import Notification as NotificationEntity
from src.application.notification.dto import NotificationCreate, NotificationUpdate
from typing import List, Optional
from datetime import datetime

class NotificationRepository(INotificationRepository):
    def get_notification(self, db: Session, notification_id: int) -> Optional[NotificationEntity]:
        db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if db_notification:
            return NotificationEntity.model_validate(db_notification.__dict__)
        return None

    def get_notifications_by_user(self, db: Session, user_id: int) -> List[NotificationEntity]:
        db_notifications = db.query(Notification).filter(Notification.user_id == user_id).all()
        return [NotificationEntity.model_validate(n.__dict__) for n in db_notifications]

    def create_notification(self, db: Session, notification_data: NotificationEntity) -> NotificationEntity:
        db_notification = Notification(
            user_id=notification_data.user_id,
            message=notification_data.message,
            is_read=notification_data.is_read,
            created_at=notification_data.created_at
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return NotificationEntity.model_validate(db_notification.__dict__)

    def update_notification(self, db: Session, notification_id: int, notification_data: NotificationEntity) -> Optional[NotificationEntity]:
        db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if db_notification:
            for key, value in notification_data.model_dump(exclude_unset=True).items():
                setattr(db_notification, key, value)
            db.commit()
            db.refresh(db_notification)
            return NotificationEntity.model_validate(db_notification.__dict__)
        return None

    def delete_notification(self, db: Session, notification_id: int) -> bool:
        db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if db_notification:
            db.delete(db_notification)
            db.commit()
            return True
        return False
