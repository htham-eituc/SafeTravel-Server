from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.notification.entities import Notification as NotificationEntity

class INotificationRepository(ABC):
    @abstractmethod
    def get_notification(self, db: Session, notification_id: int) -> Optional[NotificationEntity]:
        pass

    @abstractmethod
    def get_notifications_by_user(self, db: Session, user_id: int) -> List[NotificationEntity]:
        pass

    @abstractmethod
    def create_notification(self, db: Session, notification_data: NotificationEntity) -> NotificationEntity:
        pass

    @abstractmethod
    def update_notification(self, db: Session, notification_id: int, notification_data: NotificationEntity) -> Optional[NotificationEntity]:
        pass

    @abstractmethod
    def delete_notification(self, db: Session, notification_id: int) -> bool:
        pass
