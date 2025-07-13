from sqlalchemy import Column, String, DateTime, Text, Enum, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.database import Base
import uuid
import enum


class InterviewStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class MessageRole(enum.Enum):
    system = "system"
    assistant = "assistant"
    user = "user"


class Interview(Base):
    __tablename__ = "interviews"
    
    interview_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    group_id = Column(String(36), ForeignKey("groups.group_id"), nullable=False)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.pending, nullable=False)
    preferences_summary = Column(Text, nullable=True)  # AIが生成した要約
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # リレーション
    user = relationship("User", back_populates="interviews")
    group = relationship("Group")
    messages = relationship("Message", back_populates="interview", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    interview_id = Column(String(36), ForeignKey("interviews.interview_id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    sequence_number = Column(Integer, nullable=False)  # メッセージの順序
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # AI応答メタデータ
    is_mock = Column(String(10), nullable=True)  # AI応答がモックかどうか（"true"/"false"）
    ai_source = Column(String(20), nullable=True)  # AI応答のソース（"openai"/"mock"）
    ai_model = Column(String(50), nullable=True)  # 使用されたAIモデル
    
    # リレーション
    interview = relationship("Interview", back_populates="messages")
