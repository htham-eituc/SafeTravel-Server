from sqlalchemy.orm import Session
from src.infrastructure.trip.models import Trip
from src.domain.trip.repository_interface import ITripRepository
from src.domain.trip.entities import Trip as TripEntity
from typing import List, Optional

class TripRepository(ITripRepository):
    def get_trip(self, db: Session, trip_id: int) -> Optional[TripEntity]:
        db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if db_trip:
            return TripEntity.model_validate(db_trip.__dict__)
        return None

    def get_trips_by_user(self, db: Session, user_id: int) -> List[TripEntity]:
        db_trips = db.query(Trip).filter(Trip.user_id == user_id).all()
        return [TripEntity.model_validate(t.__dict__) for t in db_trips]

    def create_trip(self, db: Session, trip_data: TripEntity) -> TripEntity:
        db_trip = Trip(
            tripname=trip_data.tripname,
            place=trip_data.place,
            start_date=trip_data.start_date,
            end_date=trip_data.end_date,
            trip_type=trip_data.trip_type,
            have_elderly=trip_data.have_elderly,
            have_children=trip_data.have_children,
            user_id=trip_data.user_id
        )
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        return TripEntity.model_validate(db_trip.__dict__)

    def update_trip(self, db: Session, trip_id: int, trip_data: TripEntity) -> Optional[TripEntity]:
        db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if db_trip:
            for key, value in trip_data.model_dump(exclude_unset=True).items():
                setattr(db_trip, key, value)
            db.commit()
            db.refresh(db_trip)
            return TripEntity.model_validate(db_trip.__dict__)
        return None

    def delete_trip(self, db: Session, trip_id: int) -> bool:
        db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if db_trip:
            db.delete(db_trip)
            db.commit()
            return True
        return False