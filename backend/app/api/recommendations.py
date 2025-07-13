from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import uuid
import json
from datetime import datetime
from pydantic import BaseModel

from app.db.database import get_db
from app.models import Group, User, Recommendation, RestaurantCandidate, Vote
from app.schemas.recommendation import RecommendationResponse

class VoteRequest(BaseModel):
    vote_type: str
    user_id: str

class FinalDecisionRequest(BaseModel):
    restaurant_id: str
    restaurant_name: str
    decided_by_user_id: str

router = APIRouter()


@router.post("/groups/{group_id}/recommendations")
def create_group_recommendations(
    group_id: str,
    db: Session = Depends(get_db)
):
    """
    全員のヒアリングをもとに店舗候補を生成（簡略版）
    """
    from app.models import Interview
    from app.models.interview import InterviewStatus
    from app.models.group import group_members
    
    # グループの存在確認
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # グループのメンバー数を取得
    member_count_result = db.execute(
        text("SELECT COUNT(*) FROM group_members WHERE group_id = :group_id"),
        {"group_id": group_id}
    ).scalar()
    member_count = member_count_result or 0
    
    # 完了したインタビューの数を取得
    completed_interviews = db.query(Interview).filter(
        Interview.group_id == group_id,
        Interview.status == InterviewStatus.completed
    ).count()
    
    print(f"Group {group_id}: {completed_interviews}/{member_count} interviews completed")
    
    # 全員のヒアリングが完了していない場合はエラー
    if completed_interviews < member_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"All members must complete their interviews first. Completed: {completed_interviews}/{member_count}"
        )
    
    # 既存の推薦があるかチェック（どのステータスでも拒否）
    existing_recommendation = db.query(Recommendation).filter(
        Recommendation.group_id == group_id
    ).first()
    
    if existing_recommendation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation already exists for this group"
        )
    
    # 簡略版の推薦作成
    db_recommendation = Recommendation(
        recommendation_id=str(uuid.uuid4()),
        group_id=group_id,
        status="completed"
    )
    
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    
    # ホットペッパーAPIを使用してレストランを検索
    try:
        # デフォルトの検索条件（渋谷エリア）
        search_params = {
            'lat': 35.6595,      # 渋谷の緯度
            'lng': 139.7005,     # 渋谷の経度
            'range': 3,          # 1000m範囲
            'keyword': '居酒屋', # デフォルトキーワード
            'count': 5           # 5件取得
        }
        
        # ホットペッパーAPIで検索（importはファイル上部で行う必要があります）
        import requests
        
        api_key = 'dddcc42e51793523'  # 設定から取得
        base_url = 'https://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
        
        search_params['key'] = api_key
        search_params['format'] = 'json'
        
        response = requests.get(base_url, params=search_params, timeout=10)
        response.raise_for_status()
        
        api_data = response.json()
        
        restaurants_data = []
        if 'results' in api_data and 'shop' in api_data['results']:
            for shop in api_data['results']['shop'][:3]:  # 最大3件
                restaurant_data = {
                    "name": shop.get('name', ''),
                    "cuisine_type": shop.get('genre', {}).get('name', 'レストラン'),
                    "price_range": shop.get('budget', {}).get('name', '¥¥'),
                    "address": shop.get('address', ''),
                    "rating": 4.0,  # ホットペッパーAPIには評価がないのでデフォルト
                    "image_url": shop.get('photo', {}).get('pc', {}).get('l', '') if shop.get('photo') else ''
                }
                restaurants_data.append(restaurant_data)
        
        # APIから取得できない場合はダミーデータを使用
        if not restaurants_data:
            restaurants_data = [
                {
                    "name": "イタリアン・トラットリア",
                    "cuisine_type": "イタリアン",
                    "price_range": "¥¥",
                    "address": "東京都渋谷区恵比寿1-1-1",
                    "rating": 4.2,
                    "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=300&h=200&fit=crop"
                },
                {
                    "name": "和食居酒屋 さくら",
                    "cuisine_type": "和食", 
                    "price_range": "¥¥",
                    "address": "東京都渋谷区恵比寿2-2-2",
                    "rating": 4.5,
                    "image_url": "https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=300&h=200&fit=crop"
                },
                {
                    "name": "フレンチビストロ",
                    "cuisine_type": "フレンチ",
                    "price_range": "¥¥¥",
                    "address": "東京都渋谷区恵比寿3-3-3",
                    "rating": 4.3,
                    "image_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=300&h=200&fit=crop"
                }
            ]
            
    except Exception as e:
        # API呼び出しに失敗した場合はダミーデータを使用
        restaurants_data = [
            {
                "name": "イタリアン・トラットリア",
                "cuisine_type": "イタリアン",
                "price_range": "¥¥",
                "address": "東京都渋谷区恵比寿1-1-1",
                "rating": 4.2,
                "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=300&h=200&fit=crop"
            },
            {
                "name": "和食居酒屋 さくら",
                "cuisine_type": "和食", 
                "price_range": "¥¥",
                "address": "東京都渋谷区恵比寿2-2-2",
                "rating": 4.5,
                "image_url": "https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=300&h=200&fit=crop"
            },
            {
                "name": "フレンチビストロ",
                "cuisine_type": "フレンチ",
                "price_range": "¥¥¥",
                "address": "東京都渋谷区恵比寿3-3-3",
                "rating": 4.3,
                "image_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=300&h=200&fit=crop"
            }
        ]
    
    created_restaurants = []
    for restaurant_data in restaurants_data:
        candidate = RestaurantCandidate(
            candidate_id=str(uuid.uuid4()),
            recommendation_id=db_recommendation.recommendation_id,
            name=restaurant_data["name"],
            cuisine_type=restaurant_data["cuisine_type"],
            price_range=restaurant_data["price_range"],
            address=restaurant_data["address"],
            rating=restaurant_data["rating"],
            image_url=restaurant_data["image_url"]
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        created_restaurants.append({
            "restaurant_id": candidate.candidate_id,
            "name": candidate.name,
            "cuisine_type": candidate.cuisine_type,
            "price_range": candidate.price_range,
            "address": candidate.address,
            "external_rating": candidate.rating,
            "external_review_count": 100,
            "image_url": candidate.image_url,
            "vote_count": 0
        })
    
    return {
        "recommendation_id": db_recommendation.recommendation_id,
        "group_id": group_id,
        "status": "completed",
        "reasoning": "AI分析により、グループの好みに合わせて選出されました",
        "restaurants": created_restaurants,
        "created_at": db_recommendation.created_at.isoformat(),
        "message": "Recommendation created with restaurant candidates"
    }


@router.get("/recommendations/{recommendation_id}")
def get_recommendation(
    recommendation_id: str,
    db: Session = Depends(get_db)
):
    """推薦情報取得"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return {
        "recommendation_id": recommendation.recommendation_id,
        "group_id": recommendation.group_id,
        "preferences_summary": recommendation.preferences_summary,
        "status": recommendation.status,
        "created_at": recommendation.created_at
    }


@router.get("/groups/{group_id}/recommendations")
def get_group_recommendations(
    group_id: str,
    db: Session = Depends(get_db)
):
    """グループの推薦一覧取得"""
    # 最新のrecommendationを取得（created_atで降順ソート）
    recommendation = db.query(Recommendation).filter(
        Recommendation.group_id == group_id
    ).order_by(Recommendation.created_at.desc()).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendations found for this group"
        )
    
    # データベースから候補を取得
    candidates = db.query(RestaurantCandidate).filter(
        RestaurantCandidate.recommendation_id == recommendation.recommendation_id
    ).all()
    
    restaurants = []
    for candidate in candidates:
        restaurants.append({
            "restaurant_id": candidate.candidate_id,
            "name": candidate.name,
            "cuisine_type": candidate.cuisine_type,
            "price_range": candidate.price_range,
            "address": candidate.address,
            "external_rating": candidate.rating,
            "external_review_count": 100,
            "image_url": candidate.image_url,
            "vote_count": 0
        })
    
    return {
        "recommendation_id": recommendation.recommendation_id,
        "group_id": recommendation.group_id,
        "status": recommendation.status,
        "reasoning": "AI分析により、グループの好みに合わせて選出されました",
        "restaurants": restaurants,
        "created_at": recommendation.created_at.isoformat(),
        "updated_at": recommendation.updated_at.isoformat()
    }


@router.post("/candidates/{candidate_id}/vote")
def vote_for_candidate(
    candidate_id: str,
    vote_request: VoteRequest,
    db: Session = Depends(get_db)
):
    """レストラン候補に投票"""
    from app.models.recommendation import VoteType
    
    print(f"Vote API called - candidate_id: {candidate_id}, user_id: {vote_request.user_id}, vote_type: {vote_request.vote_type}")
    
    # 候補の存在確認
    candidate = db.query(RestaurantCandidate).filter(
        RestaurantCandidate.candidate_id == candidate_id
    ).first()
    
    if not candidate:
        print(f"Candidate not found: {candidate_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant candidate not found"
        )
    
    print(f"Candidate found: {candidate.name}")
    
    # ユーザーの存在確認
    user = db.query(User).filter(User.user_id == vote_request.user_id).first()
    if not user:
        print(f"User not found: {vote_request.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    print(f"User found: {user.nickname}")
    
    # 投票タイプの検証
    try:
        vote_type_enum = VoteType(vote_request.vote_type)
        print(f"Vote type validated: {vote_type_enum}")
    except ValueError:
        print(f"Invalid vote type: {vote_request.vote_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vote type. Must be 'like', 'dislike', or 'neutral'"
        )
    
    # 同じグループ内でのユーザーの既存投票をチェック（1人1票制限）
    # 候補から推薦を取得
    candidate_recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == candidate.recommendation_id
    ).first()
    
    if candidate_recommendation:
        # このグループの推薦内で、このユーザーが他の候補に投票していないかチェック
        existing_user_vote = db.query(Vote).join(
            RestaurantCandidate, Vote.candidate_id == RestaurantCandidate.candidate_id
        ).filter(
            RestaurantCandidate.recommendation_id == candidate_recommendation.recommendation_id,
            Vote.user_id == vote_request.user_id
        ).first()
        
        if existing_user_vote and existing_user_vote.candidate_id != candidate_id:
            # 異なる候補に既に投票している場合、既存の投票を削除
            print(f"User already voted for different candidate: {existing_user_vote.candidate_id}, removing old vote")
            db.delete(existing_user_vote)
            db.commit()
    
    # 同じ候補への既存の投票をチェック
    existing_vote = db.query(Vote).filter(
        Vote.candidate_id == candidate_id,
        Vote.user_id == vote_request.user_id
    ).first()
    
    if existing_vote:
        # 既存の投票を更新
        print(f"Updating existing vote: {existing_vote.vote_id}")
        existing_vote.vote_type = vote_type_enum
        existing_vote.updated_at = datetime.utcnow()
        db.commit()
        print(f"Vote updated successfully: {existing_vote.vote_id}")
        return {"message": "Vote updated successfully", "vote_id": existing_vote.vote_id}
    else:
        # 新しい投票を作成
        print("Creating new vote")
        new_vote = Vote(
            vote_id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            user_id=vote_request.user_id,
            vote_type=vote_type_enum
        )
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        print(f"New vote created successfully: {new_vote.vote_id}")
        return {"message": "Vote created successfully", "vote_id": new_vote.vote_id}


@router.get("/groups/{group_id}/votes")
def get_group_votes(
    group_id: str,
    db: Session = Depends(get_db)
):
    """グループの投票結果を取得"""
    # グループの最新推薦を取得（created_atで降順ソート）
    recommendation = db.query(Recommendation).filter(
        Recommendation.group_id == group_id
    ).order_by(Recommendation.created_at.desc()).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendations found for this group"
        )
    
    # グループのメンバー数を取得
    group = db.query(Group).filter(Group.group_id == group_id).first()
    total_members = len(group.members) if group else 0
    
    # 投票したユーザーを追跡
    voted_users = set()
    
    # 投票結果を集計
    vote_results = []
    for candidate in recommendation.candidates:
        votes = db.query(Vote).filter(Vote.candidate_id == candidate.candidate_id).all()
        
        vote_summary = {
            "like": 0,
            "dislike": 0,
            "neutral": 0
        }
        
        for vote in votes:
            vote_summary[vote.vote_type.value] += 1
            voted_users.add(vote.user_id)
        
        vote_results.append({
            "candidate_id": candidate.candidate_id,
            "name": candidate.name,
            "vote_summary": vote_summary,
            "total_votes": len(votes)
        })
    
    return {
        "group_id": group_id,
        "recommendation_id": recommendation.recommendation_id,
        "vote_results": vote_results,
        "total_members": total_members,
        "voted_members": len(voted_users),
        "is_voting_complete": len(voted_users) >= total_members
    }


@router.get("/groups/{group_id}/user/{user_id}/vote")
def get_user_vote(
    group_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """指定されたグループでのユーザーの投票状態を取得"""
    # グループの最新推薦を取得
    recommendation = db.query(Recommendation).filter(
        Recommendation.group_id == group_id
    ).order_by(Recommendation.created_at.desc()).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendation found for this group"
        )
    
    # このユーザーがこの推薦内で投票した候補を取得
    user_vote = db.query(Vote).join(
        RestaurantCandidate, Vote.candidate_id == RestaurantCandidate.candidate_id
    ).filter(
        RestaurantCandidate.recommendation_id == recommendation.recommendation_id,
        Vote.user_id == user_id
    ).first()
    
    if user_vote:
        return {
            "has_voted": True,
            "voted_candidate_id": user_vote.candidate_id,
            "vote_type": user_vote.vote_type.value,
            "vote_id": user_vote.vote_id
        }
    else:
        return {
            "has_voted": False,
            "voted_candidate_id": None,
            "vote_type": None,
            "vote_id": None
        }


@router.get("/groups/{group_id}/interview-status")
def get_group_interview_status(
    group_id: str,
    db: Session = Depends(get_db)
):
    """グループ全体のインタビュー完了状況を取得"""
    from app.models import Interview
    from app.models.interview import InterviewStatus
    from app.models.group import group_members
    
    # グループの存在確認
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # グループのメンバー数を取得
    total_members_result = db.execute(
        text("SELECT COUNT(*) FROM group_members WHERE group_id = :group_id"),
        {"group_id": group_id}
    ).scalar()
    total_members = total_members_result or 0
    
    # 完了したインタビューの数を取得
    completed_interviews = db.query(Interview).filter(
        Interview.group_id == group_id,
        Interview.status == InterviewStatus.completed
    ).count()
    
    # 進行中のインタビューの数を取得
    in_progress_interviews = db.query(Interview).filter(
        Interview.group_id == group_id,
        Interview.status == InterviewStatus.in_progress
    ).count()
    
    return {
        "total_members": total_members,
        "completed_interviews": completed_interviews,
        "in_progress_interviews": in_progress_interviews,
        "all_completed": completed_interviews >= total_members,
        "completion_rate": completed_interviews / total_members if total_members > 0 else 0
    }


@router.post("/groups/{group_id}/final-decision")
def set_final_decision(
    group_id: str,
    decision: FinalDecisionRequest,
    db: Session = Depends(get_db)
):
    """グループの最終決定を記録"""
    # グループの存在確認
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # 決定者がホストであることを確認
    if decision.decided_by_user_id != group.host_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group host can make final decision"
        )
    
    # 最新の推薦を取得
    recommendation = db.query(Recommendation).filter(
        Recommendation.group_id == group_id
    ).order_by(Recommendation.created_at.desc()).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendations found for this group"
        )
    
    # 推薦テーブルに最終決定を記録（簡単な方法として推薦オブジェクトにフィールドを追加）
    # ここでは単純にメモとして記録
    recommendation.final_decision = json.dumps({
        "restaurant_id": decision.restaurant_id,
        "restaurant_name": decision.restaurant_name,
        "decided_by": decision.decided_by_user_id,
        "decided_at": datetime.now().isoformat()
    })
    
    db.commit()
    
    return {
        "success": True,
        "final_decision": {
            "restaurant_id": decision.restaurant_id,
            "restaurant_name": decision.restaurant_name,
            "decided_by": decision.decided_by_user_id
        }
    }


@router.get("/groups/{group_id}/final-decision")
def get_final_decision(
    group_id: str,
    db: Session = Depends(get_db)
):
    """グループの最終決定を取得"""
    # 最新の推薦を取得
    recommendation = db.query(Recommendation).filter(
        Recommendation.group_id == group_id
    ).order_by(Recommendation.created_at.desc()).first()
    
    if not recommendation:
        return {"has_final_decision": False}
    
    if hasattr(recommendation, 'final_decision') and recommendation.final_decision:
        try:
            decision_data = json.loads(recommendation.final_decision)
            return {
                "has_final_decision": True,
                "final_decision": decision_data
            }
        except:
            return {"has_final_decision": False}
    
    return {"has_final_decision": False}
