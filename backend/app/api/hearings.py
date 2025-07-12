from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.database import get_db
from app.models.hearing import Hearing
from app.models.group import Group
from app.models.user import User
from app.schemas.hearing import HearingCreate, HearingUpdate, HearingResponse

router = APIRouter()


@router.post("/", response_model=HearingResponse)
def create_hearing(hearing: HearingCreate, db: Session = Depends(get_db)):
    """新しいヒアリングを作成"""
    # グループとユーザーの存在確認
    group = db.query(Group).filter(Group.group_id == hearing.group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    user = db.query(User).filter(User.user_id == hearing.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_hearing = Hearing(**hearing.dict())
    db.add(db_hearing)
    db.commit()
    db.refresh(db_hearing)
    return db_hearing


@router.get("/{hearing_id}", response_model=HearingResponse)
def get_hearing(hearing_id: uuid.UUID, db: Session = Depends(get_db)):
    """ヒアリング情報を取得"""
    hearing = db.query(Hearing).filter(Hearing.hearing_id == hearing_id).first()
    if hearing is None:
        raise HTTPException(status_code=404, detail="Hearing not found")
    return hearing


@router.put("/{hearing_id}", response_model=HearingResponse)
def update_hearing(hearing_id: uuid.UUID, hearing_update: HearingUpdate, db: Session = Depends(get_db)):
    """ヒアリング情報を更新（回答を追加など）"""
    hearing = db.query(Hearing).filter(Hearing.hearing_id == hearing_id).first()
    if hearing is None:
        raise HTTPException(status_code=404, detail="Hearing not found")
    
    for field, value in hearing_update.dict(exclude_unset=True).items():
        setattr(hearing, field, value)
    
    db.commit()
    db.refresh(hearing)
    return hearing


@router.get("/group/{group_id}", response_model=List[HearingResponse])
def get_hearings_by_group(group_id: uuid.UUID, db: Session = Depends(get_db)):
    """グループのヒアリング一覧を取得"""
    hearings = db.query(Hearing).filter(Hearing.group_id == group_id).all()
    return hearings


@router.get("/user/{user_id}", response_model=List[HearingResponse])
def get_hearings_by_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """ユーザーのヒアリング一覧を取得"""
    hearings = db.query(Hearing).filter(Hearing.user_id == user_id).all()
    return hearings


@router.get("/group/{group_id}/user/{user_id}", response_model=List[HearingResponse])
def get_hearings_by_group_and_user(group_id: uuid.UUID, user_id: uuid.UUID, db: Session = Depends(get_db)):
    """特定のグループとユーザーのヒアリング一覧を取得"""
    hearings = db.query(Hearing).filter(
        Hearing.group_id == group_id,
        Hearing.user_id == user_id
    ).all()
    return hearings

