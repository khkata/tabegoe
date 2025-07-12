from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    nickname = Column(String(50), nullable=False)
    preferences = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    groups = relationship("Group", secondary="group_members", back_populates="members")
    hearings = relationship("Hearing", back_populates="user")
    interviews = relationship("Interview", back_populates="user")
    votes = relationship("Vote", back_populates="user")