from sqlalchemy.orm import Session
from .models import AdminLog
from .admin_log_schema import AdminLogCreate, AdminLogUpdate

class AdminLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_admin_log(self, admin_log_id: int):
        return self.db.query(AdminLog).filter(AdminLog.id == admin_log_id).first()

    def get_admin_logs_by_admin(self, admin_id: int):
        return self.db.query(AdminLog).filter(AdminLog.admin_id == admin_id).all()

    def create_admin_log(self, admin_log: AdminLogCreate):
        db_admin_log = AdminLog(
            admin_id=admin_log.admin_id,
            action=admin_log.action,
            target_id=admin_log.target_id
        )
        self.db.add(db_admin_log)
        self.db.commit()
        self.db.refresh(db_admin_log)
        return db_admin_log

    def update_admin_log(self, admin_log_id: int, admin_log_update: AdminLogUpdate):
        db_admin_log = self.db.query(AdminLog).filter(AdminLog.id == admin_log_id).first()
        if db_admin_log:
            update_data = admin_log_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_admin_log, key, value)
            self.db.commit()
            self.db.refresh(db_admin_log)
        return db_admin_log

    def delete_admin_log(self, admin_log_id: int):
        db_admin_log = self.db.query(AdminLog).filter(AdminLog.id == admin_log_id).first()
        if db_admin_log:
            self.db.delete(db_admin_log)
            self.db.commit()
            return True
        return False
