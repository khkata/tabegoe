from sqlalchemy import Column, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.database import Base
import uuid
import enum


class HearingStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    skipped = "skipped"


class Hearing(Base):
    __tablename__ = "hearings"
    
    hearing_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    group_id = Column(String(36), ForeignKey('groups.group_id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(Enum(HearingStatus), default=HearingStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーションシップ
    group = relationship("Group", back_populates="hearings")
    user = relationship("User", back_populates="hearings")