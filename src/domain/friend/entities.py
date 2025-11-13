from typing import Optional
from pydantic import BaseModel

class Friend(BaseModel):
    id: Optional[int] = None
    user_id: int
    friend_user_id: int
    status: str # e.g., "pending", "accepted", "rejected"
