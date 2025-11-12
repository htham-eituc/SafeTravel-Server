from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CircleBase(BaseModel):
    circle_name: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class CircleCreate(CircleBase):
    pass

class CircleUpdate(CircleBase):
    circle_name: Optional[str] = None
    owner_id: Optional[int] = None
    status: Optional[str] = None

class CircleInDB(CircleBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
