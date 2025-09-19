# _*_ coding: utf-8 _*_
"""User Service for handling user operations."""
import logging
from typing import List, Optional
from ai_backend.database.crud.user_crud import UserCRUD
from sqlalchemy.orm import Session
from ai_backend.utils.uuid_gen import gen
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode
from datetime import datetime

logger = logging.getLogger(__name__)


class UserService:
    """사용자 서비스를 관리하는 클래스"""
    
    def __init__(self, db: Session):
        if db is None:
            raise ValueError("Database session is required")
        
        self.db = db
        self.user_crud = UserCRUD(db)
    
    def create_user(self, user_id: str, employee_id: str, name: str):
        """사용자 생성"""
        try:
            # UserCRUD 사용
                
                # 사번 중복 체크
                if self.user_crud.check_employee_id_exists(employee_id):
                    raise HandledException(
                        ResponseCode.USER_ALREADY_EXISTS, 
                        msg=f"사번 {employee_id}는 이미 사용 중입니다."
                    )
                
                # 사용자 ID 중복 체크
                if self.user_crud.get_user(user_id):
                    raise HandledException(
                        ResponseCode.USER_ALREADY_EXISTS, 
                        msg=f"사용자 ID {user_id}는 이미 사용 중입니다."
                    )
                
                user = self.user_crud.create_user(user_id, employee_id, name)
                return user
                
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            # Service Layer에서는 구체적인 예외 타입을 모르므로 일반적인 오류로 처리
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_user(self, user_id: str):
        """사용자 조회 (ID로)"""
        try:
            # UserCRUD 사용
                user = self.user_crud.get_user(user_id)
                if not user:
                    raise HandledException(ResponseCode.USER_NOT_FOUND)
                return user
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_user_by_employee_id(self, employee_id: str):
        """사용자 조회 (사번으로)"""
        try:
            # UserCRUD 사용
                user = self.user_crud.get_user_by_employee_id(employee_id)
                if not user:
                    raise HandledException(ResponseCode.USER_NOT_FOUND)
                return user
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_users(self, skip: int = 0, limit: int = 100, is_active: bool = None):
        """사용자 목록 조회"""
        try:
            # UserCRUD 사용
                users = self.user_crud.get_users(skip, limit, is_active)
                total_count = self.user_crud.get_user_count(is_active)
                return users, total_count
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def search_users(self, keyword: str, skip: int = 0, limit: int = 100):
        """사용자 검색"""
        try:
            # UserCRUD 사용
                users = self.user_crud.search_users(keyword, skip, limit)
                return users
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def update_user(self, user_id: str, name: str = None, employee_id: str = None):
        """사용자 정보 수정"""
        try:
            # UserCRUD 사용
                
                # 사용자 존재 확인
                existing_user = self.user_crud.get_user(user_id)
                if not existing_user:
                    raise HandledException(ResponseCode.USER_NOT_FOUND)
                
                # 사번 중복 체크 (변경하는 경우)
                if employee_id and employee_id != existing_user.employee_id:
                    if self.user_crud.check_employee_id_exists(employee_id):
                        raise HandledException(
                            ResponseCode.USER_ALREADY_EXISTS, 
                            msg=f"사번 {employee_id}는 이미 사용 중입니다."
                        )
                
                return self.user_crud.update_user(user_id, name, employee_id)
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def deactivate_user(self, user_id: str):
        """사용자 비활성화"""
        try:
            # UserCRUD 사용
                
                # 사용자 존재 확인
                existing_user = self.user_crud.get_user(user_id)
                if not existing_user:
                    raise HandledException(ResponseCode.USER_NOT_FOUND)
                
                return self.user_crud.deactivate_user(user_id)
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def activate_user(self, user_id: str):
        """사용자 활성화"""
        try:
            # UserCRUD 사용
                
                # 사용자 존재 확인
                existing_user = self.user_crud.get_user(user_id)
                if not existing_user:
                    raise HandledException(ResponseCode.USER_NOT_FOUND)
                
                return self.user_crud.activate_user(user_id)
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def delete_user(self, user_id: str):
        """사용자 삭제"""
        try:
            # UserCRUD 사용
                
                # 사용자 존재 확인
                existing_user = self.user_crud.get_user(user_id)
                if not existing_user:
                    raise HandledException(ResponseCode.USER_NOT_FOUND)
                
                return self.user_crud.delete_user(user_id)
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_user_count(self, is_active: bool = None):
        """사용자 수 조회"""
        try:
            # UserCRUD 사용
                return self.user_crud.get_user_count(is_active)
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_user_statistics(self):
        """사용자 통계 조회"""
        try:
            # UserCRUD 사용
                total_count = self.user_crud.get_user_count()
                active_count = self.user_crud.get_user_count(is_active=True)
                inactive_count = self.user_crud.get_user_count(is_active=False)
                
                return {
                    "total_count": total_count,
                    "active_count": active_count,
                    "inactive_count": inactive_count
                }
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
