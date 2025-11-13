from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Location(BaseModel):
    id: Optional[int] = None
    user_id: int
    latitude: float
    longitude: float
    timestamp: datetime
