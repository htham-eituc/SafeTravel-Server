from ..domain.sos_alert.schemas import SOSAlertCreate
from ..domain.sos_alert.service import SOSAlertService
from ..domain.user.service import UserService

class SOSService:
    def __init__(self):
        self.user_service = UserService()
        self.sos_alert_service = SOSAlertService()

    def send_sos_alert(self, data: SOSAlertCreate):
        user = self.user_service.get_user(data.user_id)
        if not user:
            raise ValueError("User not found")
        