from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: Optional[int] = None # Changed back to int
    name: str
    email: str
    password_hash: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
