from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    full_name: Optional[str] = None # Thêm full_name

from pydantic import Field # New import

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72) # Added length constraints

class UserUpdate(UserBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=72) # Added length constraints

class UserInDB(UserBase):
    id: int # Changed to int
    created_at: datetime

    class Config:
        from_attributes = True

class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str

class UserRegisterDTO(UserCreate):
    pass

class UserDTO(UserBase):
    id: int # Changed to int
    created_at: datetime

    class Config:
        from_attributes = True

class AuthTokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None # Changed to int
