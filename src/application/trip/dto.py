from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TripBase(BaseModel):
    user_id: int
    # Optional circle association
    circle_id: Optional[int] = None
    tripname: str
    destination: str
    start_date: datetime
    end_date: datetime
    notes: Optional[str] = None
    trip_type: str 
    have_elderly: bool = False
    have_children: bool = False

class TripDTO(TripBase):
    id: int
    circle_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True