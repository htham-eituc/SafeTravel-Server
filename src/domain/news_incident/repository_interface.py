from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from src.domain.news_incident.entities import NewsIncident as NewsIncidentEntity


class INewsIncidentRepository(ABC):
    @abstractmethod
    def upsert_by_source_url(self, db: Session, incident: NewsIncidentEntity) -> NewsIncidentEntity:
        pass

    @abstractmethod
    def get_within_radius(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float
    ) -> List[NewsIncidentEntity]:
        pass

