from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AdminLogBase(BaseModel):
    admin_id: int
    action: str
    target_id: Optional[int] = None

class AdminLogCreate(AdminLogBase):
    pass

class AdminLogUpdate(AdminLogBase):
    admin_id: Optional[int] = None
    action: Optional[str] = None
    target_id: Optional[int] = None

class AdminLogInDB(AdminLogBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
