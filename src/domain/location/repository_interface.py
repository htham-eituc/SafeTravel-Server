from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.location.entities import Location as LocationEntity

class ILocationRepository(ABC):
    @abstractmethod
    def get_location(self, db: Session, location_id: int) -> Optional[LocationEntity]:
        pass

    @abstractmethod
    def get_locations_by_user(self, db: Session, user_id: int) -> List[LocationEntity]:
        pass

    @abstractmethod
    def create_location(self, db: Session, location_data: LocationEntity) -> LocationEntity:
        pass

    @abstractmethod
    def update_location(self, db: Session, location_id: int, location_data: LocationEntity) -> Optional[LocationEntity]:
        pass

    @abstractmethod
    def delete_location(self, db: Session, location_id: int) -> bool:
        pass
