from sqlalchemy.orm import Session
from src.infrastructure.trip.models import Trip
from src.domain.trip.repository_interface import ITripRepository
from src.domain.trip.entities import Trip as TripEntity
from typing import List, Optional
from src.application.trip.dto import TripBase

class TripUseCases:
    def __init__(self, trip_repository: ITripRepository):
        self.trip_repo = trip_repository

    def get_trip(self, db: Session, trip_id: int) -> Optional[TripEntity]:
        return self.trip_repo.get_trip(db, trip_id)

    def get_trips_by_user(self, db: Session, user_id: int) -> List[TripEntity]:
        return self.trip_repo.get_trips_by_user(db, user_id)

    def create_trip(self, db: Session, trip_data: TripBase) -> TripEntity:
        trip_entity = TripEntity(
            user_id=trip_data.user_id,
            tripname=trip_data.tripname,
            destination=trip_data.destination, # Khớp với Entity
            start_date=trip_data.start_date,
            end_date=trip_data.end_date,
            notes=trip_data.notes,
            trip_type=trip_data.trip_type,     # Thêm trường này
            have_elderly=trip_data.have_elderly, # Thêm trường này
            have_children=trip_data.have_children # Thêm trường này
        )
        return self.trip_repo.create_trip(db, trip_entity)
    
    def delete_trip(self, db: Session, trip_id: int) -> None:
        self.trip_repo.delete_trip(db, trip_id)

    def update_trip(self, db: Session, trip_id: int, trip_data: TripBase) -> Optional[TripEntity]:
        trip_entity = TripEntity(
            user_id=trip_data.user_id,
            tripname=trip_data.tripname,
            destination=trip_data.destination,
            start_date=trip_data.start_date,
            end_date=trip_data.end_date,
            notes=trip_data.notes,
            trip_type=trip_data.trip_type,
            have_elderly=trip_data.have_elderly,
            have_children=trip_data.have_children
        )
        return self.trip_repo.update_trip(db, trip_id, trip_entity)