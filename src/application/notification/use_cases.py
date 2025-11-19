from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.notification.repository_interface import INotificationRepository
from src.application.notification.dto import NotificationCreate, NotificationUpdate
from src.domain.notification.entities import Notification as NotificationEntity
from datetime import datetime

class NotificationUseCases:
    def __init__(self, notification_repository: INotificationRepository):
        self.notification_repo = notification_repository

    def get_notification(self, db: Session, notification_id: int) -> Optional[NotificationEntity]:
        return self.notification_repo.get_notification(db, notification_id)

    def get_notifications_by_user(self, db: Session, user_id: int) -> List[NotificationEntity]:
        return self.notification_repo.get_notifications_by_user(db, user_id)

    def create_notification(self, db: Session, notification_data: NotificationCreate) -> NotificationEntity:
        notification_entity = NotificationEntity(
            user_id=notification_data.user_id,
            message=notification_data.message,
            is_read=notification_data.is_read,
            created_at=datetime.now()
        )
        return self.notification_repo.create_notification(db, notification_entity)

    def update_notification(self, db: Session, notification_id: int, notification_update: NotificationUpdate) -> Optional[NotificationEntity]:
        existing_notification = self.notification_repo.get_notification(db, notification_id)
        if not existing_notification:
            return None
        
        update_data = notification_update.model_dump(exclude_unset=True)
        updated_notification_entity = existing_notification.model_copy(update=update_data)
        return self.notification_repo.update_notification(db, notification_id, updated_notification_entity)

    def delete_notification(self, db: Session, notification_id: int) -> bool:
        return self.notification_repo.delete_notification(db, notification_id)
