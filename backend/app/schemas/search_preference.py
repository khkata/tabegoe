from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class SearchPreferenceCreate(BaseModel):
    """検索条件作成用スキーマ"""
    group_id: str
    user_id: str
    
    # 場所関連
    location_keyword: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    search_range: Optional[int] = 3
    
    # ジャンル・料理関連
    genre_codes: Optional[str] = None
    cuisine_preferences: Optional[str] = None
    
    # 予算関連
    budget_codes: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    
    # 人数・日時
    party_capacity: Optional[int] = None
    preferred_datetime: Optional[datetime] = None
    
    # キーワード・特徴
    keywords: Optional[str] = None
    
    # その他の条件
    other_conditions: Optional[Dict[str, Any]] = None

class SearchPreferenceUpdate(BaseModel):
    """検索条件更新用スキーマ"""
    location_keyword: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    search_range: Optional[int] = None
    genre_codes: Optional[str] = None
    cuisine_preferences: Optional[str] = None
    budget_codes: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    party_capacity: Optional[int] = None
    preferred_datetime: Optional[datetime] = None
    keywords: Optional[str] = None
    other_conditions: Optional[Dict[str, Any]] = None

class SearchPreferenceResponse(BaseModel):
    """検索条件レスポンス用スキーマ"""
    preference_id: str
    group_id: str
    user_id: str
    location_keyword: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    search_range: Optional[int]
    genre_codes: Optional[str]
    cuisine_preferences: Optional[str]
    budget_codes: Optional[str]
    budget_min: Optional[int]
    budget_max: Optional[int]
    party_capacity: Optional[int]
    preferred_datetime: Optional[datetime]
    keywords: Optional[str]
    other_conditions: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MergedSearchQuery(BaseModel):
    """マージされた検索クエリ"""
    lat: Optional[float] = None
    lng: Optional[float] = None
    range: Optional[int] = None
    keyword: Optional[str] = None
    genre: Optional[str] = None
    budget: Optional[str] = None
    party_capacity: Optional[int] = None
    
    # その他のホットペッパーAPI条件
    wifi: Optional[int] = None
    private_room: Optional[int] = None
    free_drink: Optional[int] = None
    free_food: Optional[int] = None
    card: Optional[int] = None
    non_smoking: Optional[int] = None
    parking: Optional[int] = None
    child: Optional[int] = None

class RestaurantSearchResult(BaseModel):
    """レストラン検索結果"""
    restaurants: List[Dict[str, Any]]
    total_count: int
    search_query: MergedSearchQuery
