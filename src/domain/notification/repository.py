from sqlalchemy.orm import Session
from .models import Notification
from .notification_schema import NotificationCreate, NotificationUpdate

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_notification(self, notification_id: int):
        return self.db.query(Notification).filter(Notification.id == notification_id).first()

    def get_notifications_by_user(self, user_id: int):
        return self.db.query(Notification).filter(Notification.user_id == user_id).all()

    def create_notification(self, notification: NotificationCreate):
        db_notification = Notification(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            type=notification.type,
            is_read=notification.is_read
        )
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)
        return db_notification

    def update_notification(self, notification_id: int, notification_update: NotificationUpdate):
        db_notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if db_notification:
            update_data = notification_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_notification, key, value)
            self.db.commit()
            self.db.refresh(db_notification)
        return db_notification

    def delete_notification(self, notification_id: int):
        db_notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if db_notification:
            self.db.delete(db_notification)
            self.db.commit()
            return True
        return False
