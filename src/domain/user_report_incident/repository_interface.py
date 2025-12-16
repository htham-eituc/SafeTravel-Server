from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from src.domain.user_report_incident.entities import UserReportIncident as UserReportIncidentEntity


class IUserReportIncidentRepository(ABC):
    @abstractmethod
    def create(self, db: Session, incident: UserReportIncidentEntity) -> UserReportIncidentEntity:
        pass

    @abstractmethod
    def get_within_radius(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float
    ) -> List[UserReportIncidentEntity]:
        pass

