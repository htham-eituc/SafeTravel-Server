from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FriendRequestBase(BaseModel):
    receiver_username: str

class FriendRequestCreate(FriendRequestBase):
    pass

class FriendRequestResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FriendshipResponse(BaseModel):
    id: int
    user_id: int
    friend_id: int
    created_at: datetime

    class Config:
        from_attributes = True
