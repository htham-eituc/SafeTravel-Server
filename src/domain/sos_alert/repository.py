from sqlalchemy.orm import Session
from .models import SOSAlert
from .schemas import SOSAlertCreate, SOSAlertUpdate

class SOSAlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_sos_alert(self, sos_alert_id: int):
        return self.db.query(SOSAlert).filter(SOSAlert.id == sos_alert_id).first()

    def get_sos_alerts_by_user(self, user_id: int):
        return self.db.query(SOSAlert).filter(SOSAlert.user_id == user_id).all()

    def create_sos_alert(self, sos_alert: SOSAlertCreate):
        db_sos_alert = SOSAlert(
            user_id=sos_alert.user_id,
            latitude=sos_alert.latitude,
            longitude=sos_alert.longitude,
            message=sos_alert.message,
            status=sos_alert.status
        )
        self.db.add(db_sos_alert)
        self.db.commit()
        self.db.refresh(db_sos_alert)
        return db_sos_alert

    def update_sos_alert(self, sos_alert_id: int, sos_alert_update: SOSAlertUpdate):
        db_sos_alert = self.db.query(SOSAlert).filter(SOSAlert.id == sos_alert_id).first()
        if db_sos_alert:
            update_data = sos_alert_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_sos_alert, key, value)
            self.db.commit()
            self.db.refresh(db_sos_alert)
        return db_sos_alert

    def delete_sos_alert(self, sos_alert_id: int):
        db_sos_alert = self.db.query(SOSAlert).filter(SOSAlert.id == sos_alert_id).first()
        if db_sos_alert:
            self.db.delete(db_sos_alert)
            self.db.commit()
            return True
        return False
