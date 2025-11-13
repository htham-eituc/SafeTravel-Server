from sqlalchemy.orm import Session
from src.infrastructure.location.models import Location
from src.domain.location.repository_interface import ILocationRepository
from src.domain.location.entities import Location as LocationEntity
from src.application.location.dto import LocationCreate, LocationUpdate
from typing import List, Optional
from datetime import datetime

class LocationRepository(ILocationRepository):
    def get_location(self, db: Session, location_id: int) -> Optional[LocationEntity]:
        db_location = db.query(Location).filter(Location.id == location_id).first()
        if db_location:
            return LocationEntity.model_validate(db_location.__dict__)
        return None

    def get_locations_by_user(self, db: Session, user_id: int) -> List[LocationEntity]:
        db_locations = db.query(Location).filter(Location.user_id == user_id).all()
        return [LocationEntity.model_validate(loc.__dict__) for loc in db_locations]

    def create_location(self, db: Session, location_data: LocationEntity) -> LocationEntity:
        db_location = Location(
            user_id=location_data.user_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            timestamp=location_data.timestamp
        )
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        return LocationEntity.model_validate(db_location.__dict__)

    def update_location(self, db: Session, location_id: int, location_data: LocationEntity) -> Optional[LocationEntity]:
        db_location = db.query(Location).filter(Location.id == location_id).first()
        if db_location:
            for key, value in location_data.model_dump(exclude_unset=True).items():
                setattr(db_location, key, value)
            db.commit()
            db.refresh(db_location)
            return LocationEntity.model_validate(db_location.__dict__)
        return None

    def delete_location(self, db: Session, location_id: int) -> bool:
        db_location = db.query(Location).filter(Location.id == location_id).first()
        if db_location:
            db.delete(db_location)
            db.commit()
            return True
        return False
