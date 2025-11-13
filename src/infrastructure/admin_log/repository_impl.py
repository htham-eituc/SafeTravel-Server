from sqlalchemy.orm import Session
from src.infrastructure.admin_log.models import AdminLog
from src.domain.admin_log.repository_interface import IAdminLogRepository
from src.domain.admin_log.entities import AdminLog as AdminLogEntity
from src.application.admin_log.dto import AdminLogCreate, AdminLogUpdate
from typing import List, Optional
from datetime import datetime

class AdminLogRepository(IAdminLogRepository):
    def get_admin_log(self, db: Session, admin_log_id: int) -> Optional[AdminLogEntity]:
        db_admin_log = db.query(AdminLog).filter(AdminLog.id == admin_log_id).first()
        if db_admin_log:
            return AdminLogEntity.model_validate(db_admin_log.__dict__)
        return None

    def get_admin_logs_by_admin(self, db: Session, admin_id: int) -> List[AdminLogEntity]:
        db_admin_logs = db.query(AdminLog).filter(AdminLog.admin_id == admin_id).all()
        return [AdminLogEntity.model_validate(log.__dict__) for log in db_admin_logs]

    def create_admin_log(self, db: Session, admin_log_data: AdminLogEntity) -> AdminLogEntity:
        db_admin_log = AdminLog(
            admin_id=admin_log_data.admin_id,
            action=admin_log_data.action,
            timestamp=admin_log_data.timestamp
        )
        db.add(db_admin_log)
        db.commit()
        db.refresh(db_admin_log)
        return AdminLogEntity.model_validate(db_admin_log.__dict__)

    def update_admin_log(self, db: Session, admin_log_id: int, admin_log_data: AdminLogEntity) -> Optional[AdminLogEntity]:
        db_admin_log = db.query(AdminLog).filter(AdminLog.id == admin_log_id).first()
        if db_admin_log:
            for key, value in admin_log_data.model_dump(exclude_unset=True).items():
                setattr(db_admin_log, key, value)
            db.commit()
            db.refresh(db_admin_log)
            return AdminLogEntity.model_validate(db_admin_log.__dict__)
        return None

    def delete_admin_log(self, db: Session, admin_log_id: int) -> bool:
        db_admin_log = db.query(AdminLog).filter(AdminLog.id == admin_log_id).first()
        if db_admin_log:
            db.delete(db_admin_log)
            db.commit()
            return True
        return False
