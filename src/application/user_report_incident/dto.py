from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserReportIncidentCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    latitude: float
    longitude: float
    severity: Optional[int] = Field(None, ge=0, le=100)


class UserReportIncidentInDB(BaseModel):
    id: int
    reporter_id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    latitude: float
    longitude: float
    severity: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

