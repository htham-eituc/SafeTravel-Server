from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    disabled: bool = False
    created_at: Optional[datetime] = None
