from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.group import GroupStatus


class UserSimple(BaseModel):
    user_id: str
    nickname: str
    
    class Config:
        from_attributes = True


class GroupBase(BaseModel):
    name: Optional[str] = None


class GroupCreate(GroupBase):
    host_user_id: str


class GroupUpdate(GroupBase):
    status: Optional[GroupStatus] = None


class GroupResponse(GroupBase):
    group_id: str
    host_user_id: str
    invite_code: str
    status: GroupStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GroupWithMembers(GroupResponse):
    members: List[UserSimple] = []


class GroupJoinRequest(BaseModel):
    invite_code: str
    user_id: str