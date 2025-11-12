from sqlalchemy.orm import Session
from .admin_log_repository import AdminLogRepository
from .admin_log_schema import AdminLogCreate, AdminLogUpdate
from .admin_log import AdminLog

class AdminLogService:
    def __init__(self, db: Session):
        self.admin_log_repo = AdminLogRepository(db)

    def get_admin_log(self, admin_log_id: int) -> AdminLog:
        return self.admin_log_repo.get_admin_log(admin_log_id)

    def get_admin_logs_by_admin(self, admin_id: int) -> list[AdminLog]:
        return self.admin_log_repo.get_admin_logs_by_admin(admin_id)

    def create_admin_log(self, admin_log: AdminLogCreate) -> AdminLog:
        return self.admin_log_repo.create_admin_log(admin_log)

    def update_admin_log(self, admin_log_id: int, admin_log_update: AdminLogUpdate) -> AdminLog:
        return self.admin_log_repo.update_admin_log(admin_log_id, admin_log_update)

    def delete_admin_log(self, admin_log_id: int) -> bool:
        return self.admin_log_repo.delete_admin_log(admin_log_id)
