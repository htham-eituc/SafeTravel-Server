from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class AdminLog(BaseModel):
    id: Optional[int] = None
    admin_id: int
    action: str
    timestamp: datetime
