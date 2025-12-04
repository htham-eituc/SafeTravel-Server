from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TripBase(BaseModel):
    user_id: int
    tripname: str
    destination: str
    start_date: datetime
    end_date: datetime
    notes: Optional[str] = None