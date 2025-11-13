from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.sos_alert.entities import SOSAlert as SOSAlertEntity

class ISOSAlertRepository(ABC):
    @abstractmethod
    def get_sos_alert(self, db: Session, sos_alert_id: int) -> Optional[SOSAlertEntity]:
        pass

    @abstractmethod
    def get_sos_alerts_by_user(self, db: Session, user_id: int) -> List[SOSAlertEntity]:
        pass

    @abstractmethod
    def create_sos_alert(self, db: Session, sos_alert_data: SOSAlertEntity) -> SOSAlertEntity:
        pass

    @abstractmethod
    def update_sos_alert(self, db: Session, sos_alert_id: int, sos_alert_data: SOSAlertEntity) -> Optional[SOSAlertEntity]:
        pass

    @abstractmethod
    def delete_sos_alert(self, db: Session, sos_alert_id: int) -> bool:
        pass
