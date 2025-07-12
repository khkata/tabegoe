from sqlalchemy import Column, String, DateTime, Text, Float, Integer, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.database import Base
import uuid
import enum


class RecommendationStatus(enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class VoteType(enum.Enum):
    like = "like"
    dislike = "dislike"
    neutral = "neutral"


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    recommendation_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    group_id = Column(String(36), ForeignKey("groups.group_id"), nullable=False)
    status = Column(Enum(RecommendationStatus), default=RecommendationStatus.pending)
    final_decision = Column(Text, nullable=True)  # JSON形式で最終決定を保存
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーションシップ
    group = relationship("Group", back_populates="recommendations")
    candidates = relationship("RestaurantCandidate", back_populates="recommendation")


class RestaurantCandidate(Base):
    __tablename__ = "restaurant_candidates"
    
    candidate_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    recommendation_id = Column(String(36), ForeignKey("recommendations.recommendation_id"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    rating = Column(Float, nullable=True)
    price_range = Column(String(50), nullable=True)
    cuisine_type = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    features = Column(Text, nullable=True)  # JSON形式で保存
    opening_hours = Column(String(200), nullable=True)
    contact = Column(String(100), nullable=True)
    area = Column(String(100), nullable=True)
    recommendation_reason = Column(Text, nullable=True)
    match_score = Column(Float, nullable=True)
    highlights = Column(Text, nullable=True)  # JSON形式で保存
    external_id = Column(String(255), nullable=True)
    external_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    recommendation = relationship("Recommendation", back_populates="candidates")
    votes = relationship("Vote", back_populates="candidate")


class Vote(Base):
    __tablename__ = "votes"
    
    vote_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    candidate_id = Column(String(36), ForeignKey("restaurant_candidates.candidate_id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    vote_type = Column(Enum(VoteType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーションシップ
    candidate = relationship("RestaurantCandidate", back_populates="votes")
    user = relationship("User", back_populates="votes")
    
    # 1人のユーザーが同じ候補に対して複数回投票できないようにする
    __table_args__ = (UniqueConstraint('candidate_id', 'user_id', name='unique_user_candidate_vote'),)