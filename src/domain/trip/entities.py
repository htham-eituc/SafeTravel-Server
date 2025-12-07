from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Trip(BaseModel):
    id: Optional[int] = None
    user_id: int
    # Optional link to a circle the trip belongs to
    circle_id: Optional[int] = None
    tripname: str
    destination: str 
    start_date: datetime
    end_date: datetime
    trip_type: str
    have_elderly: bool = False
    have_children: bool = False
    notes: Optional[str] = None
    created_at: Optional[datetime] = None