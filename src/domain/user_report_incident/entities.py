from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserReportIncident(BaseModel):
    id: Optional[int] = None
    reporter_id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    latitude: float
    longitude: float
    severity: Optional[int] = None
    status: str = "active"
    created_at: Optional[datetime] = None

