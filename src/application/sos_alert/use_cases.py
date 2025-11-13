from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.sos_alert.repository_interface import ISOSAlertRepository
from src.application.sos_alert.dto import SOSAlertCreate, SOSAlertUpdate
from src.domain.sos_alert.entities import SOSAlert as SOSAlertEntity
from datetime import datetime

class SOSAlertUseCases:
    def __init__(self, sos_alert_repository: ISOSAlertRepository):
        self.sos_alert_repo = sos_alert_repository

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
        return self.sos_alert_repo.create_sos_alert(db, sos_alert_entity)

    def update_sos_alert(self, db: Session, sos_alert_id: int, sos_alert_update: SOSAlertUpdate) -> Optional[SOSAlertEntity]:
        existing_alert = self.sos_alert_repo.get_sos_alert(db, sos_alert_id)
        if not existing_alert:
            return None
        
        update_data = sos_alert_update.model_dump(exclude_unset=True)
        updated_alert_entity = existing_alert.model_copy(update=update_data)
        return self.sos_alert_repo.update_sos_alert(db, sos_alert_id, updated_alert_entity)

    def delete_sos_alert(self, db: Session, sos_alert_id: int) -> bool:
        return self.sos_alert_repo.delete_sos_alert(db, sos_alert_id)
