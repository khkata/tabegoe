from sqlalchemy import Column, String, DateTime, Enum, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.database import Base
import uuid
import enum
import secrets
import string


class GroupStatus(enum.Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


def generate_invite_code():
    """6桁の招待コードを生成"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))


# グループとユーザーの多対多関係のための中間テーブル
group_members = Table(
    'group_members',
    Base.metadata,
    Column('group_id', String(36), ForeignKey('groups.group_id'), primary_key=True),
    Column('user_id', String(36), ForeignKey('users.user_id'), primary_key=True)
)


class Group(Base):
    __tablename__ = "groups"
    
    group_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=True)
    host_user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)  # ホストユーザーID追加
    invite_code = Column(String(6), unique=True, nullable=False, default=generate_invite_code, index=True)  # 招待コード追加
    status = Column(Enum(GroupStatus), default=GroupStatus.active)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーションシップ
    members = relationship("User", secondary=group_members, back_populates="groups")
    hearings = relationship("Hearing", back_populates="group")
    recommendations = relationship("Recommendation", back_populates="group")
    interviews = relationship("Interview", back_populates="group")