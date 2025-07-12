from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.group import Group
from app.models.user import User
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse, GroupWithMembers, GroupJoinRequest

router = APIRouter()


@router.post("/", response_model=GroupResponse)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    """新しいグループを作成（ホストユーザーが実行）"""
    # ホストユーザーの存在確認
    host_user = db.query(User).filter(User.user_id == group.host_user_id).first()
    if host_user is None:
        raise HTTPException(status_code=404, detail="Host user not found")
    
    # グループを作成
    db_group = Group(
        name=group.name,
        host_user_id=group.host_user_id
    )
    
    # ホストユーザーをメンバーに追加
    db_group.members.append(host_user)
    
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


@router.post("/join", response_model=GroupWithMembers)
def join_group(join_request: GroupJoinRequest, db: Session = Depends(get_db)):
    """招待コードでグループに参加"""
    # 招待コードでグループを検索
    group = db.query(Group).filter(Group.invite_code == join_request.invite_code).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    
    # ユーザーの存在確認
    user = db.query(User).filter(User.user_id == join_request.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 既にメンバーかどうか確認
    if user in group.members:
        raise HTTPException(status_code=400, detail="User is already a member of this group")
    
    # グループにユーザーを追加
    group.members.append(user)
    db.commit()
    db.refresh(group)
    
    # GroupWithMembersレスポンスを返す
    group_data = GroupWithMembers(
        group_id=group.group_id,
        name=group.name,
        invite_code=group.invite_code,
        host_user_id=group.host_user_id,
        status=group.status,
        created_at=group.created_at,
        updated_at=group.updated_at,
        members=[{
            "user_id": member.user_id,
            "nickname": member.nickname
        } for member in group.members]
    )
    
    return group_data


@router.get("/{group_id}", response_model=GroupWithMembers)
def get_group(group_id: str, db: Session = Depends(get_db)):
    """グループ情報の取得"""
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # メンバー情報を含むレスポンスを作成
    group_data = GroupWithMembers(
        group_id=group.group_id,
        name=group.name,
        host_user_id=group.host_user_id,
        invite_code=group.invite_code,
        status=group.status,
        created_at=group.created_at,
        updated_at=group.updated_at,
        members=[{
            "user_id": member.user_id,
            "nickname": member.nickname
        } for member in group.members]
    )
    
    return group_data


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(group_id: str, group_update: GroupUpdate, db: Session = Depends(get_db)):
    """グループ情報を更新"""
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    for field, value in group_update.dict(exclude_unset=True).items():
        setattr(group, field, value)
    
    db.commit()
    db.refresh(group)
    return group


@router.post("/{group_id}/members/{user_id}")
def add_member_to_group(group_id: str, user_id: str, db: Session = Depends(get_db)):
    """グループにメンバーを追加"""
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user not in group.members:
        group.members.append(user)
        db.commit()
    
    return {"message": "Member added to group successfully"}


@router.delete("/{group_id}/members/{user_id}")
def remove_member_from_group(group_id: str, user_id: str, db: Session = Depends(get_db)):
    """グループからメンバーを削除"""
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user in group.members:
        group.members.remove(user)
        db.commit()
    
    return {"message": "Member removed from group successfully"}

