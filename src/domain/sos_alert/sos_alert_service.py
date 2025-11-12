from sqlalchemy.orm import Session
from .sos_alert_repository import SOSAlertRepository
from .sos_alert_schema import SOSAlertCreate, SOSAlertUpdate
from .sos_alert import SOSAlert

class SOSAlertService:
    def __init__(self, db: Session):
        self.sos_alert_repo = SOSAlertRepository(db)

    def get_sos_alert(self, sos_alert_id: int) -> SOSAlert:
        return self.sos_alert_repo.get_sos_alert(sos_alert_id)

    def get_sos_alerts_by_user(self, user_id: int) -> list[SOSAlert]:
        return self.sos_alert_repo.get_sos_alerts_by_user(user_id)

    def create_sos_alert(self, sos_alert: SOSAlertCreate) -> SOSAlert:
        return self.sos_alert_repo.create_sos_alert(sos_alert)

    def update_sos_alert(self, sos_alert_id: int, sos_alert_update: SOSAlertUpdate) -> SOSAlert:
        return self.sos_alert_repo.update_sos_alert(sos_alert_id, sos_alert_update)

    def delete_sos_alert(self, sos_alert_id: int) -> bool:
        return self.sos_alert_repo.delete_sos_alert(sos_alert_id)
