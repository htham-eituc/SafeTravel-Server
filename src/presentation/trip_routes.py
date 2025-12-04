from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from src.application.trip.dto import TripBase, TripDTO
from src.application.dependencies import get_db_session, get_trip_use_cases, get_current_user
from src.domain.trip.entities import Trip as TripEntity
from src.application.trip.use_cases import TripUseCases

router = APIRouter()

@router.get("/trips/{trip_id}", response_model=TripDTO)
async def get_trip_by_id(
    trip_id: int,
    current_user: Annotated[TripEntity, Depends(get_current_user)],  # Ensure user is authenticated
    db: Session = Depends(get_db_session),
    trip_use_cases: TripUseCases = Depends(get_trip_use_cases)
):
    """
    Get trip details by ID.
    """
    trip = trip_use_cases.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return TripDTO.from_orm(trip)

@router.get("/users/{user_id}/trips", response_model=List[TripDTO])
async def get_trips_by_user(
    user_id: int,
    current_user: Annotated[TripEntity, Depends(get_current_user)],  # Ensure user is authenticated
    db: Session = Depends(get_db_session),
    trip_use_cases: TripUseCases = Depends(get_trip_use_cases)
):
    """
    Get all trips for a specific user.
    """
    trips = trip_use_cases.get_trips_by_user(db, user_id)
    return [TripDTO.from_orm(trip) for trip in trips]

@router.post("/trips/", response_model=TripDTO, status_code=status.HTTP_201_CREATED)
async def create_trip(
    trip_data: TripBase,
    current_user: Annotated[TripEntity, Depends(get_current_user)],  # Ensure user is authenticated
    db: Session = Depends(get_db_session),
    trip_use_cases: TripUseCases = Depends(get_trip_use_cases)
):
    """
    Create a new trip.
    """
    trip = trip_use_cases.create_trip(db, trip_data)
    return TripDTO.from_orm(trip)

@router.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: int,
    current_user: Annotated[TripEntity, Depends(get_current_user)],  # Ensure user is authenticated
    db: Session = Depends(get_db_session),
    trip_use_cases: TripUseCases = Depends(get_trip_use_cases)
):
    """
    Delete a trip by ID.
    """
    trip_use_cases.delete_trip(db, trip_id)

@router.put("/trips/{trip_id}", response_model=TripDTO)
async def update_trip(
    trip_id: int,
    trip_data: TripBase,
    current_user: Annotated[TripEntity, Depends(get_current_user)],  # Ensure user is authenticated
    db: Session = Depends(get_db_session),
    trip_use_cases: TripUseCases = Depends(get_trip_use_cases)
):
    """
    Update a trip by ID.
    """
    updated_trip = trip_use_cases.update_trip(db, trip_id, trip_data)
    if not updated_trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return TripDTO.from_orm(updated_trip)