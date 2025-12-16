from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class SOSAlertBase(BaseModel):
    user_id: int
    circle_id: Optional[int] = None # Added circle_id
    message: Optional[str] = None
    latitude: float
    longitude: float
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
        from_attributes = True

class SOSIncidentUser(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class SOSIncidentResponse(BaseModel):
    alert: SOSAlertInDB
    user: SOSIncidentUser
    sources: List[str]
