from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NewsIncident(BaseModel):
    id: Optional[int] = None
    title: str
    summary: Optional[str] = None
    category: Optional[str] = None
    location_name: Optional[str] = None
    latitude: float
    longitude: float
    source_url: str
    published_at: Optional[datetime] = None
    severity: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

