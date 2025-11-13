from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CircleMember(BaseModel):
    id: Optional[int] = None
    circle_id: int
    member_id: int
    role: str # e.g., "owner", "member", "admin"
    joined_at: Optional[datetime] = None
