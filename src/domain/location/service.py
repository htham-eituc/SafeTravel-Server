from sqlalchemy.orm import Session
from .repository import LocationRepository
from .schemas import LocationCreate, LocationUpdate
from .models import Location

class LocationService:
    def __init__(self, db: Session):
        self.location_repo = LocationRepository(db)

    def get_location(self, location_id: int) -> Location:
        return self.location_repo.get_location(location_id)

    def get_locations_by_user(self, user_id: int) -> list[Location]:
        return self.location_repo.get_locations_by_user(user_id)

    def create_location(self, location: LocationCreate) -> Location:
        return self.location_repo.create_location(location)

    def update_location(self, location_id: int, location_update: LocationUpdate) -> Location:
        return self.location_repo.update_location(location_id, location_update)

    def delete_location(self, location_id: int) -> bool:
        return self.location_repo.delete_location(location_id)
