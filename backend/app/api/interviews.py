from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
import uuid
import json
from datetime import datetime

from app.db.database import get_db
from app.models import User, Group, Interview, Message
from app.models.interview import InterviewStatus, MessageRole
from app.schemas.interview import (
    InterviewCreate, InterviewResponse, InterviewChatRequest,
    InterviewAutoCompleteRequest, MessageResponse, InterviewListResponse
)
from app.clients.openai_client import openai_client

router = APIRouter()


@router.post("/groups/{group_id}/users/{user_id}/interviews", response_model=InterviewResponse)
async def create_interview(
    group_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    ユーザーのインタビューを作成
    """
    # ユーザーとグループの存在確認
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # ユーザーがグループのメンバーかチェック
    if user not in group.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this group"
        )
    
    # 既存のインタビューをチェック
    existing_interview = db.query(Interview).filter(
        and_(
            Interview.user_id == user_id,
            Interview.group_id == group_id
        )
    ).first()
    
    if existing_interview:
        # 既存のインタビューがある場合はそれを返す（エラーではなく）
        messages = db.query(Message).filter(
            Message.interview_id == existing_interview.interview_id
        ).order_by(Message.sequence_number).all()
        
        return InterviewResponse(
            interview_id=existing_interview.interview_id,
            user_id=existing_interview.user_id,
            group_id=existing_interview.group_id,
            status=existing_interview.status,
            preferences_summary=existing_interview.preferences_summary,
            created_at=existing_interview.created_at,
            updated_at=existing_interview.updated_at,
            completed_at=existing_interview.completed_at,
            messages=[MessageResponse(
                message_id=msg.message_id,
                interview_id=msg.interview_id,
                role=msg.role,
                content=msg.content,
                sequence_number=msg.sequence_number,
                created_at=msg.created_at
            ) for msg in messages]
        )
    
    # インタビュー作成
    db_interview = Interview(
        interview_id=str(uuid.uuid4()),
        user_id=user_id,
        group_id=group_id,
        status=InterviewStatus.in_progress
    )
    
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    
    # 初期システムメッセージを作成
    initial_message = Message(
        message_id=str(uuid.uuid4()),
        interview_id=db_interview.interview_id,
        role=MessageRole.assistant,
        content="こんにちは！レストラン選びのお手伝いをさせていただきます。あなたの好みや要望を教えてください。",
        sequence_number=1
    )
    
    db.add(initial_message)
    db.commit()
    db.refresh(initial_message)
    
    return InterviewResponse(
        interview_id=db_interview.interview_id,
        user_id=db_interview.user_id,
        group_id=db_interview.group_id,
        status=db_interview.status,
        preferences_summary=db_interview.preferences_summary,
        created_at=db_interview.created_at,
        updated_at=db_interview.updated_at,
        completed_at=db_interview.completed_at,
        messages=[MessageResponse(
            message_id=initial_message.message_id,
            interview_id=initial_message.interview_id,
            role=initial_message.role,
            content=initial_message.content,
            sequence_number=initial_message.sequence_number,
            created_at=initial_message.created_at
        )]
    )


@router.get("/interviews/{interview_id}", response_model=InterviewResponse)
def get_interview(
    interview_id: str,
    db: Session = Depends(get_db)
):
    """インタビュー情報取得"""
    interview = db.query(Interview).filter(
        Interview.interview_id == interview_id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    return interview


@router.post("/interviews/{interview_id}/chat", response_model=MessageResponse)
async def chat_with_interview(
    interview_id: str,
    chat_request: InterviewChatRequest,
    db: Session = Depends(get_db)
):
    """
    インタビューでチャット
    """
    interview = db.query(Interview).filter(
        Interview.interview_id == interview_id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if interview.status != InterviewStatus.in_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is not in progress"
        )
    
    # 既存のメッセージを取得
    existing_messages = db.query(Message).filter(
        Message.interview_id == interview_id
    ).order_by(Message.sequence_number).all()
    
    next_sequence = len(existing_messages) + 1
    
    # ユーザーメッセージを保存
    user_message = Message(
        message_id=str(uuid.uuid4()),
        interview_id=interview_id,
        role=MessageRole.user,
        content=chat_request.message,
        sequence_number=next_sequence
    )
    
    db.add(user_message)
    db.commit()
    
    # OpenAI APIでレスポンス生成
    message_history = [
        {"role": msg.role.value, "content": msg.content}
        for msg in existing_messages
    ]
    message_history.append({"role": "user", "content": chat_request.message})
    
    ai_response = await openai_client.chat_completion(message_history)
    
    # AIメッセージを保存
    ai_message = Message(
        message_id=str(uuid.uuid4()),
        interview_id=interview_id,
        role=MessageRole.assistant,
        content=ai_response,
        sequence_number=next_sequence + 1
    )
    
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    return MessageResponse(
        message_id=ai_message.message_id,
        interview_id=ai_message.interview_id,
        role=ai_message.role,
        content=ai_message.content,
        sequence_number=ai_message.sequence_number,
        created_at=ai_message.created_at
    )


@router.post("/interviews/{interview_id}/complete")
async def complete_interview(
    interview_id: str,
    complete_request: InterviewAutoCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    インタビューを完了
    """
    interview = db.query(Interview).filter(
        Interview.interview_id == interview_id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if interview.status == InterviewStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is already completed"
        )
    
    # メッセージ履歴を取得
    messages = db.query(Message).filter(
        Message.interview_id == interview_id
    ).order_by(Message.sequence_number).all()
    
    # 好みを分析
    message_history = [
        {"role": msg.role.value, "content": msg.content}
        for msg in messages
    ]
    
    preferences = await openai_client.analyze_preferences(message_history)
    
    # インタビューを完了状態に更新
    interview.status = InterviewStatus.completed
    interview.preferences_summary = json.dumps(preferences, ensure_ascii=False)
    interview.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(interview)
    
    return {
        "interview_id": interview_id,
        "status": "completed",
        "preferences_summary": preferences,
        "message": "Interview completed successfully"
    }


@router.get("/groups/{group_id}/interviews", response_model=InterviewListResponse)
def get_group_interviews(
    group_id: str,
    db: Session = Depends(get_db)
):
    """グループのインタビュー一覧取得"""
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    interviews = db.query(Interview).filter(
        Interview.group_id == group_id
    ).all()
    
    return InterviewListResponse(
        interviews=interviews,
        total=len(interviews)
    )


@router.get("/users/{user_id}/interviews", response_model=InterviewListResponse)
def get_user_interviews(
    user_id: str,
    db: Session = Depends(get_db)
):
    """ユーザーのインタビュー一覧取得"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    interviews = db.query(Interview).filter(
        Interview.user_id == user_id
    ).all()
    
    return InterviewListResponse(
        interviews=interviews,
        total=len(interviews)
    )


@router.post("/", response_model=InterviewResponse)
async def create_interview_simple(
    request: InterviewCreate,
    db: Session = Depends(get_db)
):
    """
    シンプルなインタビュー作成エンドポイント
    """
    # ユーザーとグループの存在確認
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    group = db.query(Group).filter(Group.group_id == request.group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # ユーザーがグループのメンバーかチェック
    if user not in group.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this group"
        )
    
    # 既存のインタビューがあるかチェック
    existing_interview = db.query(Interview).filter(
        and_(Interview.user_id == request.user_id, Interview.group_id == request.group_id)
    ).first()
    
    if existing_interview:
        # 既存のインタビューのメッセージも取得
        messages = db.query(Message).filter(
            Message.interview_id == existing_interview.interview_id
        ).order_by(Message.sequence_number).all()
        
        return InterviewResponse(
            interview_id=existing_interview.interview_id,
            user_id=existing_interview.user_id,
            group_id=existing_interview.group_id,
            status=existing_interview.status.value,
            created_at=existing_interview.created_at,
            updated_at=existing_interview.updated_at,
            completed_at=existing_interview.completed_at,
            preferences_summary=existing_interview.preferences_summary,
            messages=[MessageResponse(
                message_id=msg.message_id,
                interview_id=msg.interview_id,
                role=msg.role,
                content=msg.content,
                sequence_number=msg.sequence_number,
                created_at=msg.created_at
            ) for msg in messages]
        )
    
    # 新しいインタビューを作成
    interview_id = str(uuid.uuid4())
    new_interview = Interview(
        interview_id=interview_id,
        user_id=request.user_id,
        group_id=request.group_id,
        status=InterviewStatus.in_progress
    )
    
    db.add(new_interview)
    
    # 初期メッセージを作成
    initial_message = Message(
        message_id=str(uuid.uuid4()),
        interview_id=interview_id,
        role=MessageRole.assistant,
        content="こんにちは！今日は美味しいお店を一緒に探しましょう。まず、どのような料理がお好みですか？"
    )
    
    db.add(initial_message)
    db.commit()
    db.refresh(new_interview)
    
    return InterviewResponse(
        interview_id=interview_id,
        user_id=request.user_id,
        group_id=request.group_id,
        status=new_interview.status.value,
        created_at=new_interview.created_at,
        updated_at=new_interview.updated_at,
        completed_at=new_interview.completed_at,
        preferences_summary=new_interview.preferences_summary,
        messages=[MessageResponse(
            message_id=initial_message.message_id,
            interview_id=initial_message.interview_id,
            role=initial_message.role,
            content=initial_message.content,
            sequence_number=initial_message.sequence_number,
            created_at=initial_message.created_at
        )]
    )


@router.post("/{interview_id}/chat", response_model=MessageResponse)
async def chat_simple(
    interview_id: str,
    chat_request: InterviewChatRequest,
    db: Session = Depends(get_db)
):
    """
    シンプルなチャットエンドポイント
    """
    # インタビューの存在確認
    interview = db.query(Interview).filter(Interview.interview_id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # インタビューが進行中かチェック
    if interview.status != InterviewStatus.in_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is not in progress"
        )
    
    # 既存のメッセージを取得
    existing_messages = db.query(Message).filter(
        Message.interview_id == interview_id
    ).order_by(Message.sequence_number).all()
    
    next_sequence = len(existing_messages) + 1
    
    # ユーザーメッセージを保存
    user_message = Message(
        message_id=str(uuid.uuid4()),
        interview_id=interview_id,
        role=MessageRole.user,
        content=chat_request.message,
        sequence_number=next_sequence
    )
    
    db.add(user_message)
    db.commit()
    
    # OpenAI APIでレスポンス生成
    try:
        message_history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in existing_messages
        ]
        message_history.append({"role": "user", "content": chat_request.message})
        
        ai_response = await openai_client.chat_completion(message_history)
        
        # AIレスポンスメッセージを保存
        ai_message = Message(
            message_id=str(uuid.uuid4()),
            interview_id=interview_id,
            role=MessageRole.assistant,
            content=ai_response,
            sequence_number=next_sequence + 1
        )
        
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        return MessageResponse(
            message_id=ai_message.message_id,
            interview_id=ai_message.interview_id,
            role=ai_message.role,
            content=ai_message.content,
            sequence_number=ai_message.sequence_number,
            created_at=ai_message.created_at
        )
        
    except Exception as e:
        # AI APIエラー時のフォールバック
        fallback_response = "申し訳ございません。一時的にAIサービスに接続できません。再度お試しください。"
        
        ai_message = Message(
            message_id=str(uuid.uuid4()),
            interview_id=interview_id,
            role=MessageRole.assistant,
            content=fallback_response,
            sequence_number=next_sequence + 1
        )
        
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        return MessageResponse(
            message_id=ai_message.message_id,
            interview_id=ai_message.interview_id,
            role=ai_message.role,
            content=ai_message.content,
            sequence_number=ai_message.sequence_number,
            created_at=ai_message.created_at
        )


@router.post("/{interview_id}/complete")
async def complete_interview_simple(
    interview_id: str,
    db: Session = Depends(get_db)
):
    """
    シンプルなインタビュー完了エンドポイント
    """
    # インタビューの存在確認
    interview = db.query(Interview).filter(Interview.interview_id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # インタビューメッセージを取得
    messages = db.query(Message).filter(
        Message.interview_id == interview_id
    ).order_by(Message.sequence_number).all()
    
    # メッセージの内容から好みを分析
    try:
        message_contents = [msg.content for msg in messages if msg.role == MessageRole.user]
        analysis_prompt = f"""
        以下のユーザーの発言から、レストランの好みを分析してください：
        
        {chr(10).join(message_contents)}
        
        以下の形式で分析結果を返してください：
        - 好みの料理ジャンル: 
        - 予算範囲: 
        - 特別な要望: 
        - アレルギー情報: 
        - 優先事項:
        """
        
        analysis_result = await openai_client.analyze_preferences(analysis_prompt)
        
        # インタビューを完了状態に更新
        interview.status = InterviewStatus.completed
        interview.preferences_summary = analysis_result
        interview.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(interview)
        
        return {
            "interview_id": interview_id,
            "status": "completed",
            "preferences_summary": analysis_result
        }
        
    except Exception as e:
        # AI分析失敗時のフォールバック
        basic_analysis = "ユーザーの好みを記録しました。詳細な分析はAIサービス復旧後に実行されます。"
        
        interview.status = InterviewStatus.completed
        interview.preferences_summary = basic_analysis
        interview.completed_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "interview_id": interview_id,
            "status": "completed",
            "preferences_summary": basic_analysis
        }


@router.get("/groups/{group_id}/interview-status")
def get_group_interview_status(
    group_id: str,
    db: Session = Depends(get_db)
):
    """グループのインタビュー完了状況を取得"""
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # グループメンバーのインタビュー状況を確認
    member_status = []
    total_members = len(group.members)
    completed_interviews = 0
    
    for member in group.members:
        interview = db.query(Interview).filter(
            Interview.user_id == member.user_id,
            Interview.group_id == group_id
        ).first()
        
        if interview:
            status = interview.status.value
            if interview.status == InterviewStatus.completed:
                completed_interviews += 1
        else:
            status = "not_started"
        
        member_status.append({
            "user_id": member.user_id,
            "nickname": member.nickname,
            "interview_status": status
        })
    
    all_completed = completed_interviews == total_members
    
    return {
        "group_id": group_id,
        "total_members": total_members,
        "completed_interviews": completed_interviews,
        "all_completed": all_completed,
        "member_status": member_status
    }

