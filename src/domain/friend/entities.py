from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class FriendRequest(BaseModel):
    id: Optional[int] = None
    sender_id: int
    receiver_id: int
    status: str = "pending"  # "pending", "accepted", "rejected"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Friendship(BaseModel):
    id: Optional[int] = None
    user_id: int
    friend_id: int
    created_at: Optional[datetime] = None
