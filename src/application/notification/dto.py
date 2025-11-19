from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool = False

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(NotificationBase):
    user_id: Optional[int] = None
    title: Optional[str] = None
    message: Optional[str] = None
    type: Optional[str] = None
    is_read: Optional[bool] = None

class NotificationInDB(NotificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
