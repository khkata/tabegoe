from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class InterviewStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class MessageRole(str, Enum):
    system = "system"
    assistant = "assistant"
    user = "user"


# Message schemas
class MessageBase(BaseModel):
    role: MessageRole
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    message_id: str
    interview_id: str
    sequence_number: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Interview schemas
class InterviewBase(BaseModel):
    user_id: str
    group_id: str


class InterviewCreate(InterviewBase):
    pass


class InterviewResponse(InterviewBase):
    interview_id: str
    status: InterviewStatus
    preferences_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True


class InterviewChatRequest(BaseModel):
    message: str = Field(..., description="ユーザーからのメッセージ")


class InterviewAutoCompleteRequest(BaseModel):
    force_complete: bool = Field(default=False, description="強制完了フラグ")


class InterviewListResponse(BaseModel):
    interviews: List[InterviewResponse]
    total: int
    
    class Config:
        from_attributes = True
