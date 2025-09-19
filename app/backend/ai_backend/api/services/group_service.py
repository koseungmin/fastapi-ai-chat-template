# _*_ coding: utf-8 _*_
"""Group Service for handling group operations."""
import logging
from typing import List, Optional, Tuple
from ai_backend.database.crud.group_crud import GroupCRUD, GroupMemberCRUD
from sqlalchemy.orm import Session
from ai_backend.utils.uuid_gen import gen
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode
from datetime import datetime

logger = logging.getLogger(__name__)


class GroupService:
    """그룹 서비스를 관리하는 클래스"""
    
    def __init__(self, db: Session):
        if db is None:
            raise ValueError("Database session is required")
        
        self.db = db
        self.group_crud = GroupCRUD(db)
        self.member_crud = GroupMemberCRUD(db)
    
    def create_group(self, group_name: str, owner_id: str, description: str = None, 
                    max_members: int = None):
        """그룹 생성"""
        try:
            # 그룹명 중복 체크
            if self.group_crud.check_group_name_exists(group_name):
                raise HandledException(
                    ResponseCode.GROUP_ALREADY_EXISTS, 
                    msg=f"그룹명 '{group_name}'은 이미 사용 중입니다."
                )
            
            # 그룹 ID 생성
            group_id = gen()
            
            # 그룹 생성
            group = self.group_crud.create_group(
                group_id=group_id,
                group_name=group_name,
                description=description,
                owner_id=owner_id,
                max_members=max_members
            )
            
            return group
                
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_group(self, group_id: str):
        """그룹 조회 (ID로)"""
        try:
            group = self.group_crud.get_group(group_id)
            if not group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            return group
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_group_by_name(self, group_name: str):
        """그룹 조회 (그룹명으로)"""
        try:
            group = self.group_crud.get_group_by_name(group_name)
            if not group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            return group
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_groups(self, skip: int = 0, limit: int = 100, is_active: bool = None, 
                   owner_id: str = None):
        """그룹 목록 조회"""
        try:
            groups = self.group_crud.get_groups(skip, limit, is_active, owner_id)
            total_count = self.group_crud.get_group_count(is_active, owner_id)
            return groups, total_count
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def search_groups(self, keyword: str, skip: int = 0, limit: int = 100):
        """그룹 검색"""
        try:
            groups = self.group_crud.search_groups(keyword, skip, limit)
            return groups
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def update_group(self, group_id: str, group_name: str = None, 
                    description: str = None, max_members: int = None):
        """그룹 정보 수정"""
        try:
            # 그룹 존재 확인
            existing_group = self.group_crud.get_group(group_id)
            if not existing_group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            
            # 그룹명 중복 체크 (변경하는 경우)
            if group_name and group_name != existing_group.group_name:
                if self.group_crud.check_group_name_exists(group_name, group_id):
                    raise HandledException(
                        ResponseCode.GROUP_ALREADY_EXISTS, 
                        msg=f"그룹명 '{group_name}'은 이미 사용 중입니다."
                    )
            
            return self.group_crud.update_group(group_id, group_name, description, max_members)
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def deactivate_group(self, group_id: str):
        """그룹 비활성화"""
        try:
            # 그룹 존재 확인
            existing_group = self.group_crud.get_group(group_id)
            if not existing_group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            
            return self.group_crud.deactivate_group(group_id)
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def activate_group(self, group_id: str):
        """그룹 활성화"""
        try:
            # 그룹 존재 확인
            existing_group = self.group_crud.get_group(group_id)
            if not existing_group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            
            return self.group_crud.activate_group(group_id)
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def delete_group(self, group_id: str):
        """그룹 삭제"""
        try:
            # 그룹 존재 확인
            existing_group = self.group_crud.get_group(group_id)
            if not existing_group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            
            return self.group_crud.delete_group(group_id)
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_group_count(self, is_active: bool = None, owner_id: str = None):
        """그룹 수 조회"""
        try:
            return self.group_crud.get_group_count(is_active, owner_id)
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_group_statistics(self):
        """그룹 통계 조회"""
        try:
            total_count = self.group_crud.get_group_count()
            active_count = self.group_crud.get_group_count(is_active=True)
            inactive_count = self.group_crud.get_group_count(is_active=False)
            
            return {
                "total_count": total_count,
                "active_count": active_count,
                "inactive_count": inactive_count
            }
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_group_detail(self, group_id: str):
        """그룹 상세 정보 조회 (멤버 포함)"""
        try:
            # 그룹 정보 조회
            group = self.group_crud.get_group(group_id)
            if not group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            
            # 멤버 목록 조회
            members = self.member_crud.get_group_members(group_id)
            
            return group, members
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    # 멤버 관련 메서드들
    def add_group_member(self, group_id: str, user_id: str, role: str = 'member'):
        """그룹 멤버 추가"""
        try:
            # 그룹 존재 확인
            group = self.group_crud.get_group(group_id)
            if not group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            
            # 이미 멤버인지 확인
            if self.member_crud.check_user_in_group(group_id, user_id):
                raise HandledException(
                    ResponseCode.GROUP_MEMBER_ALREADY_EXISTS,
                    msg="이미 그룹의 멤버입니다."
                )
            
            # 최대 멤버 수 확인
            if group.max_members:
                current_count = self.member_crud.get_group_member_count(group_id)
                if current_count >= group.max_members:
                    raise HandledException(
                        ResponseCode.GROUP_MAX_MEMBERS_EXCEEDED,
                        msg=f"그룹의 최대 멤버 수({group.max_members})를 초과했습니다."
                    )
            
            # 멤버 추가
            member_id = gen()
            member = self.member_crud.add_group_member(member_id, group_id, user_id, role)
            
            return member
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_group_members(self, group_id: str, skip: int = 0, limit: int = 100):
        """그룹 멤버 목록 조회"""
        try:
            # 그룹 존재 확인
            group = self.group_crud.get_group(group_id)
            if not group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            
            members = self.member_crud.get_group_members(group_id, skip, limit)
            total_count = self.member_crud.get_group_member_count(group_id)
            
            return members, total_count
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_user_groups(self, user_id: str, skip: int = 0, limit: int = 100):
        """사용자가 속한 그룹 목록 조회"""
        try:
            members = self.member_crud.get_user_groups(user_id, skip, limit)
            return members
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def update_member_role(self, group_id: str, user_id: str, role: str):
        """그룹 멤버 역할 변경"""
        try:
            # 그룹 존재 확인
            group = self.group_crud.get_group(group_id)
            if not group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            
            # 멤버 존재 확인
            member = self.member_crud.get_group_member(group_id, user_id)
            if not member:
                raise HandledException(ResponseCode.GROUP_MEMBER_NOT_FOUND)
            
            return self.member_crud.update_member_role(group_id, user_id, role)
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def remove_group_member(self, group_id: str, user_id: str):
        """그룹 멤버 제거"""
        try:
            # 그룹 존재 확인
            group = self.group_crud.get_group(group_id)
            if not group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            
            # 멤버 존재 확인
            member = self.member_crud.get_group_member(group_id, user_id)
            if not member:
                raise HandledException(ResponseCode.GROUP_MEMBER_NOT_FOUND)
            
            # 소유자는 제거할 수 없음
            if member.role == 'owner':
                raise HandledException(
                    ResponseCode.GROUP_OWNER_CANNOT_BE_REMOVED,
                    msg="그룹 소유자는 제거할 수 없습니다."
                )
            
            return self.member_crud.remove_group_member(group_id, user_id)
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def check_user_permission(self, group_id: str, user_id: str, required_role: str = None):
        """사용자 권한 확인"""
        try:
            # 그룹 존재 확인
            group = self.group_crud.get_group(group_id)
            if not group:
                raise HandledException(ResponseCode.GROUP_NOT_FOUND)
            
            # 멤버 확인
            member = self.member_crud.get_group_member(group_id, user_id)
            if not member:
                raise HandledException(ResponseCode.GROUP_MEMBER_NOT_FOUND)
            
            # 권한 확인
            if required_role:
                user_role = self.member_crud.check_user_role_in_group(group_id, user_id, required_role)
                if not user_role:
                    raise HandledException(
                        ResponseCode.GROUP_INSUFFICIENT_PERMISSION,
                        msg=f"'{required_role}' 권한이 필요합니다."
                    )
            
            return member
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
