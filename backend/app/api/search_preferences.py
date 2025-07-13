from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
import logging

from ..db.database import get_db
from ..models.search_preference import UserSearchPreference
from ..schemas.search_preference import (
    SearchPreferenceCreate, 
    SearchPreferenceUpdate, 
    SearchPreferenceResponse,
    MergedSearchQuery,
    RestaurantSearchResult
)
from ..clients.hotpepper_client import hotpepper_client

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/groups/{group_id}/users/{user_id}/search-preferences", 
             response_model=SearchPreferenceResponse)
def create_search_preference(
    group_id: str,
    user_id: str,
    preference: SearchPreferenceCreate,
    db: Session = Depends(get_db)
):
    """ユーザーの検索条件を作成"""
    
    # 既存の条件があれば削除
    existing = db.query(UserSearchPreference).filter(
        UserSearchPreference.group_id == group_id,
        UserSearchPreference.user_id == user_id
    ).first()
    
    if existing:
        db.delete(existing)
        db.commit()
    
    # 新しい検索条件を作成
    db_preference = UserSearchPreference(
        preference_id=str(uuid.uuid4()),
        group_id=group_id,
        user_id=user_id,
        location_keyword=preference.location_keyword,
        lat=preference.lat,
        lng=preference.lng,
        search_range=preference.search_range,
        genre_codes=preference.genre_codes,
        cuisine_preferences=preference.cuisine_preferences,
        budget_codes=preference.budget_codes,
        budget_min=preference.budget_min,
        budget_max=preference.budget_max,
        party_capacity=preference.party_capacity,
        preferred_datetime=preference.preferred_datetime,
        keywords=preference.keywords,
        other_conditions=preference.other_conditions
    )
    
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    
    return db_preference

@router.get("/groups/{group_id}/users/{user_id}/search-preferences",
            response_model=SearchPreferenceResponse)
def get_user_search_preference(
    group_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """ユーザーの検索条件を取得"""
    
    preference = db.query(UserSearchPreference).filter(
        UserSearchPreference.group_id == group_id,
        UserSearchPreference.user_id == user_id
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="検索条件が見つかりません"
        )
    
    return preference

@router.get("/groups/{group_id}/search-preferences",
            response_model=List[SearchPreferenceResponse])
def get_group_search_preferences(
    group_id: str,
    db: Session = Depends(get_db)
):
    """グループ全体の検索条件を取得"""
    
    preferences = db.query(UserSearchPreference).filter(
        UserSearchPreference.group_id == group_id
    ).all()
    
    return preferences

@router.post("/groups/{group_id}/search-restaurants",
             response_model=RestaurantSearchResult)
def search_restaurants_for_group(
    group_id: str,
    db: Session = Depends(get_db)
):
    """グループの条件を統合してレストラン検索"""
    
    # グループの全ユーザーの検索条件を取得
    preferences = db.query(UserSearchPreference).filter(
        UserSearchPreference.group_id == group_id
    ).all()
    
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="検索条件が見つかりません"
        )
    
    try:
        # ユーザー条件をマージして検索クエリを作成
        user_preferences_data = []
        for pref in preferences:
            pref_data = {
                'lat': pref.lat,
                'lng': pref.lng,
                'range': pref.search_range,
                'keyword': pref.keywords,
                'genre': pref.genre_codes,
                'budget': pref.budget_codes,
                'party_capacity': pref.party_capacity
            }
            
            # その他の条件を追加
            if pref.other_conditions:
                pref_data.update(pref.other_conditions)
            
            user_preferences_data.append(pref_data)
        
        # 条件をマージ
        merged_params = hotpepper_client.merge_user_preferences(user_preferences_data)
        
        # ホットペッパーAPIで検索
        search_results = hotpepper_client.search_restaurants(merged_params)
        
        # 結果を変換
        restaurants = []
        if 'results' in search_results and 'shop' in search_results['results']:
            for shop in search_results['results']['shop']:
                restaurant = hotpepper_client.convert_to_restaurant_data(shop)
                restaurants.append(restaurant)
        
        # レスポンス作成
        merged_query = MergedSearchQuery(**merged_params)
        
        return {
            "restaurants": restaurants,
            "total_count": len(restaurants),
            "search_query": merged_query
        }
        
    except Exception as e:
        logger.error(f"Restaurant search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"レストラン検索でエラーが発生しました: {str(e)}"
        )

@router.put("/groups/{group_id}/users/{user_id}/search-preferences",
            response_model=SearchPreferenceResponse)
def update_search_preference(
    group_id: str,
    user_id: str,
    preference_update: SearchPreferenceUpdate,
    db: Session = Depends(get_db)
):
    """ユーザーの検索条件を更新"""
    
    existing = db.query(UserSearchPreference).filter(
        UserSearchPreference.group_id == group_id,
        UserSearchPreference.user_id == user_id
    ).first()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="検索条件が見つかりません"
        )
    
    # 更新フィールドを適用
    for field, value in preference_update.dict(exclude_unset=True).items():
        setattr(existing, field, value)
    
    db.commit()
    db.refresh(existing)
    
    return existing
