# _*_ coding: utf-8 _*_
"""Group CRUD operations with database."""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List
from datetime import datetime
from ai_backend.database.models.group_models import Group, GroupMember
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode
import logging

logger = logging.getLogger(__name__)


class GroupCRUD:
    """Group 관련 CRUD 작업을 처리하는 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_group(self, group_id: str, group_name: str, owner_id: str, 
                    description: str = None, max_members: int = None) -> Group:
        """그룹 생성"""
        try:
            group = Group(
                group_id=group_id,
                group_name=group_name,
                description=description,
                owner_id=owner_id,
                max_members=max_members,
                create_dt=datetime.now(),
                is_active=True
            )
            self.db.add(group)
            self.db.commit()
            self.db.refresh(group)
            
            # 그룹 생성자도 멤버로 추가
            self.add_group_member(group_id, owner_id, owner_id, 'owner')
            
            return group
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_group(self, group_id: str) -> Optional[Group]:
        """그룹 조회 (ID로)"""
        try:
            return self.db.query(Group).filter(
                and_(Group.group_id == group_id, Group.is_deleted == False)
            ).first()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_group_by_name(self, group_name: str) -> Optional[Group]:
        """그룹 조회 (그룹명으로)"""
        try:
            return self.db.query(Group).filter(
                and_(Group.group_name == group_name, Group.is_deleted == False)
            ).first()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_groups(self, skip: int = 0, limit: int = 100, is_active: bool = None, 
                   owner_id: str = None) -> List[Group]:
        """그룹 목록 조회"""
        try:
            query = self.db.query(Group).filter(Group.is_deleted == False)
            
            if is_active is not None:
                query = query.filter(Group.is_active == is_active)
            
            if owner_id is not None:
                query = query.filter(Group.owner_id == owner_id)
            
            return query.order_by(desc(Group.create_dt)).offset(skip).limit(limit).all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def search_groups(self, keyword: str, skip: int = 0, limit: int = 100) -> List[Group]:
        """그룹 검색 (그룹명으로)"""
        try:
            return self.db.query(Group).filter(
                and_(
                    Group.is_deleted == False,
                    Group.group_name.contains(keyword)
                )
            ).order_by(desc(Group.create_dt)).offset(skip).limit(limit).all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_group(self, group_id: str, group_name: str = None, 
                    description: str = None, max_members: int = None) -> Optional[Group]:
        """그룹 정보 수정"""
        try:
            group = self.get_group(group_id)
            if group:
                if group_name is not None:
                    group.group_name = group_name
                if description is not None:
                    group.description = description
                if max_members is not None:
                    group.max_members = max_members
                
                group.update_dt = datetime.now()
                self.db.commit()
                self.db.refresh(group)
            return group
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def deactivate_group(self, group_id: str) -> bool:
        """그룹 비활성화 (소프트 삭제)"""
        try:
            group = self.get_group(group_id)
            if group:
                group.is_active = False
                group.update_dt = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def activate_group(self, group_id: str) -> bool:
        """그룹 활성화"""
        try:
            group = self.get_group(group_id)
            if group:
                group.is_active = True
                group.update_dt = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def delete_group(self, group_id: str) -> bool:
        """그룹 삭제 (하드 삭제)"""
        try:
            group = self.get_group(group_id)
            if group:
                # 먼저 모든 멤버 삭제
                self.db.query(GroupMember).filter(
                    GroupMember.group_id == group_id
                ).delete()
                
                group.is_deleted = True
                group.update_dt = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_group_count(self, is_active: bool = None, owner_id: str = None) -> int:
        """그룹 수 조회"""
        try:
            query = self.db.query(Group).filter(Group.is_deleted == False)
            
            if is_active is not None:
                query = query.filter(Group.is_active == is_active)
            
            if owner_id is not None:
                query = query.filter(Group.owner_id == owner_id)
            
            return query.count()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def check_group_name_exists(self, group_name: str, exclude_group_id: str = None) -> bool:
        """그룹명 중복 체크"""
        try:
            query = self.db.query(Group).filter(
                and_(Group.group_name == group_name, Group.is_deleted == False)
            )
            
            if exclude_group_id:
                query = query.filter(Group.group_id != exclude_group_id)
            
            return query.first() is not None
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)


class GroupMemberCRUD:
    """Group Member 관련 CRUD 작업을 처리하는 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add_group_member(self, member_id: str, group_id: str, user_id: str, role: str) -> GroupMember:
        """그룹 멤버 추가"""
        try:
            member = GroupMember(
                member_id=member_id,
                group_id=group_id,
                user_id=user_id,
                role=role,
                join_dt=datetime.now(),
                is_active=True
            )
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)
            return member
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_group_member(self, group_id: str, user_id: str) -> Optional[GroupMember]:
        """그룹 멤버 조회"""
        try:
            return self.db.query(GroupMember).filter(
                and_(
                    GroupMember.group_id == group_id,
                    GroupMember.user_id == user_id,
                    GroupMember.is_deleted == False
                )
            ).first()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_group_members(self, group_id: str, skip: int = 0, limit: int = 100) -> List[GroupMember]:
        """그룹 멤버 목록 조회"""
        try:
            return self.db.query(GroupMember).filter(
                and_(GroupMember.group_id == group_id, GroupMember.is_deleted == False)
            ).order_by(desc(GroupMember.join_dt)).offset(skip).limit(limit).all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_user_groups(self, user_id: str, skip: int = 0, limit: int = 100) -> List[GroupMember]:
        """사용자가 속한 그룹 목록 조회"""
        try:
            return self.db.query(GroupMember).filter(
                and_(GroupMember.user_id == user_id, GroupMember.is_deleted == False)
            ).order_by(desc(GroupMember.join_dt)).offset(skip).limit(limit).all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_member_role(self, group_id: str, user_id: str, role: str) -> Optional[GroupMember]:
        """그룹 멤버 역할 변경"""
        try:
            member = self.get_group_member(group_id, user_id)
            if member:
                member.role = role
                member.update_dt = datetime.now()
                self.db.commit()
                self.db.refresh(member)
            return member
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def remove_group_member(self, group_id: str, user_id: str) -> bool:
        """그룹 멤버 제거 (소프트 삭제)"""
        try:
            member = self.get_group_member(group_id, user_id)
            if member:
                member.is_deleted = True
                member.update_dt = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_group_member_count(self, group_id: str) -> int:
        """그룹 멤버 수 조회"""
        try:
            return self.db.query(GroupMember).filter(
                and_(GroupMember.group_id == group_id, GroupMember.is_deleted == False)
            ).count()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def check_user_in_group(self, group_id: str, user_id: str) -> bool:
        """사용자가 그룹에 속해있는지 확인"""
        try:
            member = self.get_group_member(group_id, user_id)
            return member is not None
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def check_user_role_in_group(self, group_id: str, user_id: str, required_role: str = None) -> Optional[str]:
        """사용자의 그룹 내 역할 확인"""
        try:
            member = self.get_group_member(group_id, user_id)
            if member:
                if required_role is None:
                    return member.role
                return member.role if member.role == required_role else None
            return None
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
