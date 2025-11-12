from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SOSAlertBase(BaseModel):
    user_id: int
    latitude: float
    longitude: float
    message: Optional[str] = None
    status: str = "pending"

class SOSAlertCreate(SOSAlertBase):
    pass

class SOSAlertUpdate(SOSAlertBase):
    user_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    message: Optional[str] = None
    status: Optional[str] = None
    resolved_at: Optional[datetime] = None

class SOSAlertInDB(SOSAlertBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        orm_mode = True
