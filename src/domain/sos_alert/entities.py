from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class SOSAlert(BaseModel):
    id: Optional[int] = None
    user_id: int
    circle_id: Optional[int] = None
    message: str
    latitude: float
    longitude: float
    status: str # e.g., "pending", "active", "resolved"
    created_at: Optional[datetime] = None
