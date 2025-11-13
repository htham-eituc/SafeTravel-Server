from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.location.repository_interface import ILocationRepository
from src.application.location.dto import LocationCreate, LocationUpdate
from src.domain.location.entities import Location as LocationEntity
from datetime import datetime

class LocationUseCases:
    def __init__(self, location_repository: ILocationRepository):
        self.location_repo = location_repository

    def get_location(self, db: Session, location_id: int) -> Optional[LocationEntity]:
        return self.location_repo.get_location(db, location_id)

    def get_locations_by_user(self, db: Session, user_id: int) -> List[LocationEntity]:
        return self.location_repo.get_locations_by_user(db, user_id)

    def create_location(self, db: Session, location_data: LocationCreate) -> LocationEntity:
        location_entity = LocationEntity(
            user_id=location_data.user_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            timestamp=datetime.now() # Assuming timestamp is set at creation
        )
        return self.location_repo.create_location(db, location_entity)

    def update_location(self, db: Session, location_id: int, location_update: LocationUpdate) -> Optional[LocationEntity]:
        existing_location = self.location_repo.get_location(db, location_id)
        if not existing_location:
            return None
        
        update_data = location_update.model_dump(exclude_unset=True)
        updated_location_entity = existing_location.model_copy(update=update_data)
        return self.location_repo.update_location(db, location_id, updated_location_entity)

    def delete_location(self, db: Session, location_id: int) -> bool:
        return self.location_repo.delete_location(db, location_id)
