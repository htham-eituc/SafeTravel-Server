from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Incident(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    latitude: float
    longitude: float
    severity: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
