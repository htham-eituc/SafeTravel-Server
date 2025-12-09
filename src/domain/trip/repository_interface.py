from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.trip.entities import Trip as TripEntity

class ITripRepository(ABC):
    @abstractmethod
    def get_trip(self, db: Session, trip_id: int) -> Optional[TripEntity]:
        pass

    @abstractmethod
    def get_trips_by_user(self, db: Session, user_id: int) -> List[TripEntity]:
        pass

    @abstractmethod
    def create_trip(self, db: Session, trip_data: TripEntity) -> TripEntity:
        pass

    @abstractmethod
    def update_trip(self, db: Session, trip_id: int, trip_data: TripEntity) -> Optional[TripEntity]:
        pass

    @abstractmethod
    def delete_trip(self, db: Session, trip_id: int) -> bool:
        pass