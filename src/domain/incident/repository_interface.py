from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.incident.entities import Incident as IncidentEntity


class IIncidentRepository(ABC):
    @abstractmethod
    def create(self, db: Session, incident: IncidentEntity) -> IncidentEntity:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, incident_id: int) -> Optional[IncidentEntity]:
        pass

    @abstractmethod
    def get_within_radius(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float
    ) -> List[IncidentEntity]:
        pass
