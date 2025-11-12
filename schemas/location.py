from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LocationBase(BaseModel):
    user_id: int
    latitude: float
    longitude: float
    speed: Optional[float] = None
    accuracy: Optional[float] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(LocationBase):
    user_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    speed: Optional[float] = None
    accuracy: Optional[float] = None

class LocationInDB(LocationBase):
    id: int
    recorded_at: datetime

    class Config:
        orm_mode = True
