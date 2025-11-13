from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from src.domain.admin_log.entities import AdminLog as AdminLogEntity

class IAdminLogRepository(ABC):
    @abstractmethod
    def get_admin_log(self, db: Session, admin_log_id: int) -> Optional[AdminLogEntity]:
        pass

    @abstractmethod
    def get_admin_logs_by_admin(self, db: Session, admin_id: int) -> List[AdminLogEntity]:
        pass

    @abstractmethod
    def create_admin_log(self, db: Session, admin_log_data: AdminLogEntity) -> AdminLogEntity:
        pass

    @abstractmethod
    def update_admin_log(self, db: Session, admin_log_id: int, admin_log_data: AdminLogEntity) -> Optional[AdminLogEntity]:
        pass

    @abstractmethod
    def delete_admin_log(self, db: Session, admin_log_id: int) -> bool:
        pass
