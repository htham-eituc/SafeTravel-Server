from sqlalchemy.orm import Session

from typing import Optional

from src.domain.user.repository_interface import IUserRepository
from src.domain.friend.repository_interface import IFriendRepository
from src.domain.sos_alert.repository_interface import ISOSAlertRepository
from src.application.sos_alert.dto import SOSAlertCreate
from src.domain.sos_alert.entities import SOSAlert as SOSAlertEntity

class SOSService:
    def __init__(self):
        self.userService = IUserRepository()
        self.friendService = IFriendRepository()
        self.sosService = ISOSAlertRepository()
        pass
    def send_sos(self, db: Session, data: SOSAlertCreate) -> Optional[SOSAlertEntity]:
        user = self.userService.get_user_by_id(data.user_id)
        if not user:
            raise ValueError("User not found")
        else:
            # get circle please !!!
            alert = self.sosService.create_sos_alert(db, data)
            return alert