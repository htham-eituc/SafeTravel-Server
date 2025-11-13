from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Circle(BaseModel):
    id: Optional[int] = None
    circle_name: str
    description: Optional[str] = None
    owner_id: int
    status: str = "active"
    created_at: Optional[datetime] = None
