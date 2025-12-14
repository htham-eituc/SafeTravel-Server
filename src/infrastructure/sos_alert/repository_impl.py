from sqlalchemy.orm import Session
from src.infrastructure.sos_alert.models import SOSAlert
from src.domain.sos_alert.repository_interface import ISOSAlertRepository
from src.domain.sos_alert.entities import SOSAlert as SOSAlertEntity
from typing import List, Optional

class SOSAlertRepository(ISOSAlertRepository):
    def get_sos_alert(self, db: Session, sos_alert_id: int) -> Optional[SOSAlertEntity]:
        db_sos_alert = db.query(SOSAlert).filter(SOSAlert.id == sos_alert_id).first()
        if db_sos_alert:
            return SOSAlertEntity.model_validate(db_sos_alert.__dict__)
        return None

    def get_sos_alerts_by_user(self, db: Session, user_id: int) -> List[SOSAlertEntity]:
        db_sos_alerts = db.query(SOSAlert).filter(SOSAlert.user_id == user_id).all()
        return [SOSAlertEntity.model_validate(s.__dict__) for s in db_sos_alerts]

    def get_sos_alerts_by_user_ids(self, db: Session, user_ids: List[int]) -> List[SOSAlertEntity]:
        if not user_ids:
            return []
        db_sos_alerts = db.query(SOSAlert).filter(SOSAlert.user_id.in_(user_ids)).all()
        return [SOSAlertEntity.model_validate(s.__dict__) for s in db_sos_alerts]

    def get_sos_alerts_within_radius(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float
    ) -> List[SOSAlertEntity]:
        lat_min = latitude - radius
        lat_max = latitude + radius
        lon_min = longitude - radius
        lon_max = longitude + radius

        db_sos_alerts = db.query(SOSAlert).filter(
            SOSAlert.latitude.between(lat_min, lat_max),
            SOSAlert.longitude.between(lon_min, lon_max)
        ).all()
        return [SOSAlertEntity.model_validate(s.__dict__) for s in db_sos_alerts]

    def create_sos_alert(self, db: Session, sos_alert_data: SOSAlertEntity) -> SOSAlertEntity:
        db_sos_alert = SOSAlert(
            user_id=sos_alert_data.user_id,
            circle_id=sos_alert_data.circle_id,
            message=sos_alert_data.message,
            latitude=sos_alert_data.latitude,
            longitude=sos_alert_data.longitude,
            status=sos_alert_data.status,
            created_at=sos_alert_data.created_at,
            resolved_at=sos_alert_data.resolved_at
        )
        db.add(db_sos_alert)
        db.commit()
        db.refresh(db_sos_alert)
        return SOSAlertEntity.model_validate(db_sos_alert.__dict__)

    def update_sos_alert(self, db: Session, sos_alert_id: int, sos_alert_data: SOSAlertEntity) -> Optional[SOSAlertEntity]:
        db_sos_alert = db.query(SOSAlert).filter(SOSAlert.id == sos_alert_id).first()
        if db_sos_alert:
            for key, value in sos_alert_data.model_dump(exclude_unset=True).items():
                setattr(db_sos_alert, key, value)
            db.commit()
            db.refresh(db_sos_alert)
            return SOSAlertEntity.model_validate(db_sos_alert.__dict__)
        return None

    def delete_sos_alert(self, db: Session, sos_alert_id: int) -> bool:
        db_sos_alert = db.query(SOSAlert).filter(SOSAlert.id == sos_alert_id).first()
        if db_sos_alert:
            db.delete(db_sos_alert)
            db.commit()
            return True
        return False
