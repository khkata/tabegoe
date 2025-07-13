from sqlalchemy import Column, String, Float, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db.database import Base

class UserSearchPreference(Base):
    """ユーザーの検索条件を保存するモデル"""
    __tablename__ = "user_search_preferences"

    preference_id = Column(String, primary_key=True, index=True)
    group_id = Column(String, ForeignKey("groups.group_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    
    # 場所関連
    location_keyword = Column(String, nullable=True)  # エリア名（渋谷、新宿など）
    lat = Column(Float, nullable=True)  # 緯度
    lng = Column(Float, nullable=True)  # 経度
    search_range = Column(Integer, default=3)  # 検索範囲（1-5）
    
    # ジャンル・料理関連
    genre_codes = Column(Text, nullable=True)  # ジャンルコード（カンマ区切り）
    cuisine_preferences = Column(Text, nullable=True)  # 料理の好み（フリーテキスト）
    
    # 予算関連
    budget_codes = Column(Text, nullable=True)  # 予算コード（カンマ区切り）
    budget_min = Column(Integer, nullable=True)  # 最低予算
    budget_max = Column(Integer, nullable=True)  # 最高予算
    
    # 人数・日時
    party_capacity = Column(Integer, nullable=True)  # 希望人数
    preferred_datetime = Column(DateTime, nullable=True)  # 希望日時
    
    # キーワード・特徴
    keywords = Column(Text, nullable=True)  # フリーワードキーワード
    
    # その他の条件（JSONで保存）
    other_conditions = Column(JSON, nullable=True)  # WiFi、個室など
    
    # メタデータ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    # group = relationship("Group", back_populates="search_preferences")
    # user = relationship("User", back_populates="search_preferences")
