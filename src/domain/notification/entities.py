from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Notification(BaseModel):
    id: Optional[int] = None
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool = False
    created_at: Optional[datetime] = None
