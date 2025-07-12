from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    nickname: str
    preferences: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    preferences: Optional[str] = None


class UserResponse(UserBase):
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AnonymousUserCreate(BaseModel):
    nickname: str