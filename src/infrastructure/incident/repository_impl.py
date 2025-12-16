
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from src.domain.incident.entities import Incident as IncidentEntity
from src.domain.incident.repository_interface import IIncidentRepository
from src.infrastructure.incident.models import Incident


class IncidentRepository(IIncidentRepository):
    def create(self, db: Session, incident: IncidentEntity) -> IncidentEntity:
        db_incident = Incident(**incident.model_dump())
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)
        return IncidentEntity.model_validate(db_incident.__dict__)

    def get_by_id(self, db: Session, incident_id: int) -> Optional[IncidentEntity]:
        db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if db_incident:
            return IncidentEntity.model_validate(db_incident.__dict__)
        return None

    def get_within_radius(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float  # in kilometers
    ) -> List[IncidentEntity]:
        """
        Get incidents within a certain radius using the Haversine formula.
        """
        # Earth radius in kilometers
        earth_radius = 6371

        # Convert latitude and longitude to radians
        lat_rad = func.radians(latitude)
        lon_rad = func.radians(longitude)
        db_lat_rad = func.radians(Incident.latitude)
        db_lon_rad = func.radians(Incident.longitude)

        # Haversine formula
        dlon = db_lon_rad - lon_rad
        dlat = db_lat_rad - lat_rad
        
        # FIX: Use func.power(x, 2) instead of x ** 2
        # You can also use (func.sin(dlat / 2) * func.sin(dlat / 2)) if power causes dialect issues
        a = func.power(func.sin(dlat / 2), 2) + \
            func.cos(lat_rad) * func.cos(db_lat_rad) * func.power(func.sin(dlon / 2), 2)
            
        c = 2 * func.atan2(func.sqrt(a), func.sqrt(1 - a))
        distance = earth_radius * c

        incidents = db.query(Incident).filter(distance <= radius).all()
        return [IncidentEntity.model_validate(i.__dict__) for i in incidents]

    def delete(self, db: Session, incident_id: int) -> bool:
        db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if db_incident:
            db.delete(db_incident)
            db.commit()
            return True
        return False
