from sqlalchemy.orm import Session
from .location import Location
from .location_schema import LocationCreate, LocationUpdate

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_location(self, location_id: int):
        return self.db.query(Location).filter(Location.id == location_id).first()

    def get_locations_by_user(self, user_id: int):
        return self.db.query(Location).filter(Location.user_id == user_id).all()

    def create_location(self, location: LocationCreate):
        db_location = Location(
            user_id=location.user_id,
            latitude=location.latitude,
            longitude=location.longitude,
            speed=location.speed,
            accuracy=location.accuracy
        )
        self.db.add(db_location)
        self.db.commit()
        self.db.refresh(db_location)
        return db_location

    def update_location(self, location_id: int, location_update: LocationUpdate):
        db_location = self.db.query(Location).filter(Location.id == location_id).first()
        if db_location:
            update_data = location_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_location, key, value)
            self.db.commit()
            self.db.refresh(db_location)
        return db_location

    def delete_location(self, location_id: int):
        db_location = self.db.query(Location).filter(Location.id == location_id).first()
        if db_location:
            self.db.delete(db_location)
            self.db.commit()
            return True
        return False
