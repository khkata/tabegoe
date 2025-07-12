from pydantic import BaseModel, field_validator
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum
import json


class RecommendationStatus(str, Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class VoteType(str, Enum):
    like = "like"
    dislike = "dislike"
    neutral = "neutral"


# Restaurant Candidate Schemas
class RestaurantCandidateBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None
    price_range: Optional[str] = None
    cuisine_type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    opening_hours: Optional[str] = None
    contact: Optional[str] = None
    area: Optional[str] = None
    recommendation_reason: Optional[str] = None
    match_score: Optional[float] = None
    highlights: Optional[List[str]] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    image_url: Optional[str] = None


class RestaurantCandidateCreate(RestaurantCandidateBase):
    recommendation_id: str


class RestaurantCandidateResponse(RestaurantCandidateBase):
    candidate_id: str
    recommendation_id: str
    created_at: datetime
    
    @field_validator('features', mode='before')
    @classmethod
    def parse_features(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v if v is not None else []
    
    @field_validator('highlights', mode='before')
    @classmethod
    def parse_highlights(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v if v is not None else []
    
    class Config:
        from_attributes = True


class RestaurantCandidateWithVotes(RestaurantCandidateResponse):
    votes: List["VoteResponse"] = []


# Vote Schemas
class VoteBase(BaseModel):
    vote_type: VoteType


class VoteCreate(VoteBase):
    candidate_id: str
    user_id: str


class VoteResponse(VoteBase):
    vote_id: str
    candidate_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VoteUpdate(BaseModel):
    vote_type: Optional[VoteType] = None


# Recommendation Schemas
class RecommendationBase(BaseModel):
    group_id: str


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationResponse(RecommendationBase):
    recommendation_id: str
    status: RecommendationStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RecommendationWithCandidates(RecommendationResponse):
    candidates: List[RestaurantCandidateResponse] = []


# Request/Response Schemas
class GenerateRecommendationRequest(BaseModel):
    group_id: str
    max_recommendations: Optional[int] = 5


class VoteRequest(BaseModel):
    candidate_id: str
    user_id: str
    vote_type: VoteType


class VoteResultResponse(BaseModel):
    candidate_id: str
    candidate_name: str
    like_count: int
    dislike_count: int
    neutral_count: int
    total_votes: int


class RecommendationListResponse(BaseModel):
    recommendations: List[RecommendationResponse]
    total_count: int


class RecommendationWithVotesResponse(RecommendationResponse):
    candidates: List[RestaurantCandidateWithVotes] = []


# 循環インポートを避けるため、型の更新
RestaurantCandidateWithVotes.model_rebuild()
