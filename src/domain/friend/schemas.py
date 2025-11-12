from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FriendBase(BaseModel):
    user_id: int
    friend_id: int

class FriendCreate(FriendBase):
    pass

class Friend(FriendBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
