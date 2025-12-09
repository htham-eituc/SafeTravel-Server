from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.admin_log.repository_interface import IAdminLogRepository
from src.application.admin_log.dto import AdminLogCreate, AdminLogUpdate
from src.domain.admin_log.entities import AdminLog as AdminLogEntity
from datetime import datetime

class AdminLogUseCases:
    def __init__(self, admin_log_repository: IAdminLogRepository):
        self.admin_log_repository = admin_log_repository

    def get_admin_log(self, db: Session, admin_log_id: int) -> Optional[AdminLogEntity]:
        return self.admin_log_repository.get_admin_log(db, admin_log_id)

    def get_admin_logs_by_admin(self, db: Session, admin_id: int) -> List[AdminLogEntity]:
        return self.admin_log_repository.get_admin_logs_by_admin(db, admin_id)

    def create_admin_log(self, db: Session, admin_log_data: AdminLogCreate) -> AdminLogEntity:
        admin_log_entity = AdminLogEntity(
            admin_id=admin_log_data.admin_id,
            action=admin_log_data.action,
            target_id=admin_log_data.target_id # Added target_id
        )
        return self.admin_log_repository.create_admin_log(db, admin_log_entity)

    def update_admin_log(self, db: Session, admin_log_id: int, admin_log_update: AdminLogUpdate) -> Optional[AdminLogEntity]:
        existing_log = self.admin_log_repository.get_admin_log(db, admin_log_id)
        if not existing_log:
            return None
        
        update_data = admin_log_update.model_dump(exclude_unset=True)
        updated_log_entity = existing_log.model_copy(update=update_data)
        return self.admin_log_repository.update_admin_log(db, admin_log_id, updated_log_entity)

    def delete_admin_log(self, db: Session, admin_log_id: int) -> bool:
        return self.admin_log_repository.delete_admin_log(db, admin_log_id)
