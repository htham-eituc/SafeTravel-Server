from pydantic import BaseModel
from typing import Optional

class CircleMemberBase(BaseModel):
    circle_id: int
    member_id: int
    role: str

class CircleMemberCreate(CircleMemberBase):
    pass

class CircleMemberUpdate(CircleMemberBase):
    circle_id: Optional[int] = None
    member_id: Optional[int] = None
    role: Optional[str] = None

class CircleMemberInDB(CircleMemberBase):
    id: int

    class Config:
        orm_mode = True
