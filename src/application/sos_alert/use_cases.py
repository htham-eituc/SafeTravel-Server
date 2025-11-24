from sqlalchemy.orm import Session
from typing import List, Optional
from src.domain.sos_alert.repository_interface import ISOSAlertRepository
from src.application.sos_alert.dto import SOSAlertCreate, SOSAlertUpdate
from src.domain.sos_alert.entities import SOSAlert as SOSAlertEntity
from datetime import datetime

from src.application.notification.use_cases import NotificationUseCases
from src.application.notification.dto import NotificationCreate
from src.domain.user.repository_interface import IUserRepository
from src.domain.friend.repository_interface import IFriendRepository
from src.domain.circle.repository_interface import ICircleRepository
from src.domain.circle.member_repository_interface import ICircleMemberRepository

class SOSAlertUseCases:
    def __init__(
        self,
        sos_alert_repository: ISOSAlertRepository,
        notification_use_cases: NotificationUseCases,
        user_repository: IUserRepository,
        friend_repository: IFriendRepository,
        circle_repository: ICircleRepository,
        circle_member_repository: ICircleMemberRepository
    ):
        self.sos_alert_repo = sos_alert_repository
        self.notification_use_cases = notification_use_cases
        self.user_repo = user_repository
        self.friend_repo = friend_repository
        self.circle_repo = circle_repository
        self.circle_member_repo = circle_member_repository

    def get_sos_alert(self, db: Session, sos_alert_id: int) -> Optional[SOSAlertEntity]:
        return self.sos_alert_repo.get_sos_alert(db, sos_alert_id)

    def get_sos_alerts_by_user(self, db: Session, user_id: int) -> List[SOSAlertEntity]:
        return self.sos_alert_repo.get_sos_alerts_by_user(db, user_id)

    def create_sos_alert(self, db: Session, sos_alert_data: SOSAlertCreate) -> SOSAlertEntity:
        sos_alert_entity = SOSAlertEntity(
            user_id=sos_alert_data.user_id,
            circle_id=sos_alert_data.circle_id,
            message=sos_alert_data.message,
            latitude=sos_alert_data.latitude,
            longitude=sos_alert_data.longitude,
            status=sos_alert_data.status,
            created_at=datetime.now()
        )
        created_alert = self.sos_alert_repo.create_sos_alert(db, sos_alert_entity)

        # Get the sender's username once
        sender_user = self.user_repo.get_user_by_id(db, sos_alert_data.user_id)
        sender_username = sender_user.username if sender_user else "Unknown User"

        # Send notifications to friends
        friends = self.friend_repo.get_user_friends(db, sos_alert_data.user_id)
        for friend in friends:
            notification_message = f"Your friend {sender_username} has sent an SOS alert!"
            notification_data = NotificationCreate(
                user_id=friend.id,
                title="SOS Alert from Friend",
                message=notification_message,
                type="SOS_FRIEND",
                is_read=False
            )
            self.notification_use_cases.create_notification(db, notification_data)

        # Send notifications to active circle members
        active_circle = self.circle_repo.get_active_circle_by_owner_id(db, sos_alert_data.user_id)
        if active_circle:
            circle_members = self.circle_member_repo.get_circle_members_by_circle_id(db, active_circle.id)
            for member in circle_members:
                if member.member_id != sos_alert_data.user_id: # Don't notify the sender
                    notification_message = f"A member of your active circle has sent an SOS alert!"
                    notification_data = NotificationCreate(
                        user_id=member.member_id,
                        title="SOS Alert from Circle",
                        message=notification_message,
                        type="SOS_CIRCLE",
                        is_read=False
                    )
                    self.notification_use_cases.create_notification(db, notification_data)

        return created_alert

    def update_sos_alert(self, db: Session, sos_alert_id: int, sos_alert_update: SOSAlertUpdate) -> Optional[SOSAlertEntity]:
        existing_alert = self.sos_alert_repo.get_sos_alert(db, sos_alert_id)
        if not existing_alert:
            return None
        
        update_data = sos_alert_update.model_dump(exclude_unset=True)
        updated_alert_entity = existing_alert.model_copy(update=update_data)
        return self.sos_alert_repo.update_sos_alert(db, sos_alert_id, updated_alert_entity)

    def delete_sos_alert(self, db: Session, sos_alert_id: int) -> bool:
        return self.sos_alert_repo.delete_sos_alert(db, sos_alert_id)
