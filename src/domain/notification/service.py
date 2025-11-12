from sqlalchemy.orm import Session
from .repository import NotificationRepository
from .schemas import NotificationCreate, NotificationUpdate
from .models import Notification

class NotificationService:
    def __init__(self, db: Session):
        self.notification_repo = NotificationRepository(db)

    def get_notification(self, notification_id: int) -> Notification:
        return self.notification_repo.get_notification(notification_id)

    def get_notifications_by_user(self, user_id: int) -> list[Notification]:
        return self.notification_repo.get_notifications_by_user(user_id)

    def create_notification(self, notification: NotificationCreate) -> Notification:
        return self.notification_repo.create_notification(notification)

    def update_notification(self, notification_id: int, notification_update: NotificationUpdate) -> Notification:
        return self.notification_repo.update_notification(notification_id, notification_update)

    def delete_notification(self, notification_id: int) -> bool:
        return self.notification_repo.delete_notification(notification_id)
