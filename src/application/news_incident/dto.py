from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NewsIncidentBase(BaseModel):
    title: str
    summary: Optional[str] = None
    category: Optional[str] = None
    location_name: Optional[str] = None
    latitude: float
    longitude: float
    source_url: str
    published_at: Optional[datetime] = None
    severity: Optional[int] = Field(None, ge=0, le=100)


class NewsIncidentInDB(NewsIncidentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NewsIncidentExtractRequest(BaseModel):
    query: str = Field(..., description="Query context, e.g. 'Vietnam' or 'Ho Chi Minh City'")
    days: int = Field(3, ge=1, le=30, description="Lookback window in days")
    max_items: int = Field(20, ge=1, le=100, description="Maximum incidents to extract")

