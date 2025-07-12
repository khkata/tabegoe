from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.hearing import HearingStatus


class HearingBase(BaseModel):
    question: str
    answer: Optional[str] = None


class HearingCreate(HearingBase):
    group_id: str
    user_id: str


class HearingUpdate(BaseModel):
    answer: Optional[str] = None
    status: Optional[HearingStatus] = None


class HearingResponse(HearingBase):
    hearing_id: str
    group_id: str
    user_id: str
    status: HearingStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
