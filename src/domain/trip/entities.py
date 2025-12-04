from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Trip(BaseModel):
    id: Optional[int] = None
    user_id: int
    tripname: str
    place: str
    start_date: datetime
    end_date: datetime
    trip_type: str  # change to enum later
    have_elderly: bool = False
    have_children: bool = False
    created_at: Optional[datetime] = None