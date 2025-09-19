# _*_ coding: utf-8 _*_
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.sql.expression import func, true, false
from ai_backend.database.base import Base

__all__ = [
    "Group",
    "GroupMember",
]


class Group(Base):
    __tablename__ = "GROUPS"
    
    group_id = Column('GROUP_ID', String(50), primary_key=True)  # 그룹 ID
    group_name = Column('GROUP_NAME', String(100), nullable=False)  # 그룹명
    description = Column('DESCRIPTION', Text, nullable=True)  # 그룹 설명
    owner_id = Column('OWNER_ID', String(50), nullable=False)  # 그룹 소유자 ID
    max_members = Column('MAX_MEMBERS', Integer, nullable=True)  # 최대 멤버 수
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())  # 생성일시
    update_dt = Column('UPDATE_DT', DateTime, nullable=True)  # 수정일시
    is_active = Column('IS_ACTIVE', Boolean, nullable=False, server_default=true())  # 활성 상태
    is_deleted = Column('IS_DELETED', Boolean, nullable=False, server_default=false())  # 삭제 여부


class GroupMember(Base):
    __tablename__ = "GROUP_MEMBERS"
    
    member_id = Column('MEMBER_ID', String(50), primary_key=True)  # 멤버 ID (UUID)
    group_id = Column('GROUP_ID', String(50), nullable=False)  # 그룹 ID
    user_id = Column('USER_ID', String(50), nullable=False)  # 사용자 ID
    role = Column('ROLE', String(20), nullable=False, default='member')  # 역할 (owner, admin, member)
    join_dt = Column('JOIN_DT', DateTime, nullable=False, server_default=func.now())  # 가입일시
    update_dt = Column('UPDATE_DT', DateTime, nullable=True)  # 수정일시
    is_active = Column('IS_ACTIVE', Boolean, nullable=False, server_default=true())  # 활성 상태
    is_deleted = Column('IS_DELETED', Boolean, nullable=False, server_default=false())  # 삭제 여부
