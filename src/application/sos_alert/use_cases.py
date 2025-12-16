from sqlalchemy.orm import Session
from typing import List, Optional
from src.domain.sos_alert.repository_interface import ISOSAlertRepository
from src.application.sos_alert.dto import (
    SOSAlertCreate,
    SOSAlertUpdate,
    SOSIncidentResponse,
    SOSIncidentUser,
    SOSAlertInDB
)
from src.domain.sos_alert.entities import SOSAlert as SOSAlertEntity
from datetime import datetime

MAX_SOS_MESSAGE_LEN = 255


def _truncate_message(message: str | None) -> str | None:
    if message is None:
        return None
    message = message.strip()
    if len(message) <= MAX_SOS_MESSAGE_LEN:
        return message
    return message[: MAX_SOS_MESSAGE_LEN - 1].rstrip() + "…"


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

    def get_incidents_for_map(
        self,
        db: Session,
        user_id: int,
        latitude: float,
        longitude: float,
        radius: float = 0.5
    ) -> List[SOSIncidentResponse]:
        if radius <= 0:
            raise ValueError("Radius must be greater than 0.")

        friend_users = self.friend_repo.get_friends_by_user_id(db, user_id)
        friend_ids = {friend.id for friend in friend_users if friend and friend.id is not None}
        friend_ids.discard(user_id)

        active_circle_ids = {
            circle.id for circle in self.circle_repo.get_circles_by_owner(db, user_id)
            if circle.status == "active"
        }

        member_entries = self.circle_member_repo.get_circle_members_by_member(db, user_id)
        for membership in member_entries:
            if membership.circle_id in active_circle_ids:
                continue
            circle = self.circle_repo.get_circle(db, membership.circle_id)
            if circle and circle.status == "active":
                active_circle_ids.add(circle.id)

        circle_member_ids = set()
        for circle_id in active_circle_ids:
            members = self.circle_member_repo.get_circle_members_by_circle(db, circle_id)
            circle_member_ids.update(member.member_id for member in members if member.member_id is not None)
        circle_member_ids.discard(user_id)

        target_user_ids = list(friend_ids.union(circle_member_ids))
        network_alerts = self.sos_alert_repo.get_sos_alerts_by_user_ids(db, target_user_ids)
        nearby_alerts = self.sos_alert_repo.get_sos_alerts_within_radius(db, latitude, longitude, radius)

        incident_store = {}
        inactive_statuses = {"resolved", "false_alarm"}

        def add_alert(alert: SOSAlertEntity, source: str):
            if not alert or alert.id is None:
                return
            if alert.user_id == user_id:
                return
            if alert.status in inactive_statuses:
                return
            entry = incident_store.setdefault(alert.id, {"alert": alert, "sources": set()})
            entry["sources"].add(source)

        for alert in network_alerts:
            if alert.user_id in friend_ids:
                add_alert(alert, "friend")
            if alert.user_id in circle_member_ids:
                add_alert(alert, "circle")
            if alert.user_id not in friend_ids and alert.user_id not in circle_member_ids:
                add_alert(alert, "friend_or_circle")

        for alert in nearby_alerts:
            add_alert(alert, "nearby")

        user_ids = {entry["alert"].user_id for entry in incident_store.values()}
        user_map = {}
        for uid in user_ids:
            user = self.user_repo.get_user_by_id(db, uid)
            if user:
                user_map[uid] = user

        incidents: List[SOSIncidentResponse] = []
        for entry in incident_store.values():
            alert_entity = entry["alert"]
            alert_dto = SOSAlertInDB.model_validate(alert_entity.model_dump())
            user = user_map.get(alert_entity.user_id)
            if not user:
                continue
            incident_user = SOSIncidentUser(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                avatar_url=user.avatar_url
            )
            incidents.append(
                SOSIncidentResponse(
                    alert=alert_dto,
                    user=incident_user,
                    sources=sorted(entry["sources"])
                )
            )

        return incidents

    def create_sos_alert(self, db: Session, sos_alert_data: SOSAlertCreate) -> SOSAlertEntity:
        sos_alert_entity = SOSAlertEntity(
            user_id=sos_alert_data.user_id,
            circle_id=sos_alert_data.circle_id,
            message=_truncate_message(sos_alert_data.message),
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
        friends = self.friend_repo.get_friends_by_user_id(db, sos_alert_data.user_id)
        for friend in friends:
            notification_message = f"Your friend {sender_username} has sent an SOS alert!"
            notification_data = NotificationCreate(
                user_id=friend.id,
                title="SOS Alert from Friend", # Added title
                message=notification_message,
                type="SOS_FRIEND", # Added type
                is_read=False
            )
            self.notification_use_cases.create_notification(db, notification_data)

        # Send notifications to active circle members
        active_circle = self.circle_repo.get_active_circle_by_owner_id(db, sos_alert_data.user_id)
        if active_circle:
            circle_members = self.circle_member_repo.get_circle_members_by_circle(db, active_circle.id)
            for member in circle_members:
                if member.member_id != sos_alert_data.user_id: # Don't notify the sender
                    notification_message = f"A member of your active circle has sent an SOS alert!"
                    notification_data = NotificationCreate(
                        user_id=member.member_id,
                        title="SOS Alert from Circle", # Added title
                        message=notification_message,
                        type="SOS_CIRCLE", # Added type
                        is_read=False
                    )
                    self.notification_use_cases.create_notification(db, notification_data)

        return created_alert

    def update_sos_alert(self, db: Session, sos_alert_id: int, sos_alert_update: SOSAlertUpdate) -> Optional[SOSAlertEntity]:
        existing_alert = self.sos_alert_repo.get_sos_alert(db, sos_alert_id)
        if not existing_alert:
            return None
        
        update_data = sos_alert_update.model_dump(exclude_unset=True)
        if "message" in update_data:
            update_data["message"] = _truncate_message(update_data["message"])
        updated_alert_entity = existing_alert.model_copy(update=update_data)
        return self.sos_alert_repo.update_sos_alert(db, sos_alert_id, updated_alert_entity)

    def delete_sos_alert(self, db: Session, sos_alert_id: int) -> bool:
        return self.sos_alert_repo.delete_sos_alert(db, sos_alert_id)
