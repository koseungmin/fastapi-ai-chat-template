# _*_ coding: utf-8 _*_
"""User CRUD operations with database."""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List
from datetime import datetime
from ai_backend.database.models.user_models import User
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode
import logging

logger = logging.getLogger(__name__)


class UserCRUD:
    """User 관련 CRUD 작업을 처리하는 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_id: str, employee_id: str, name: str) -> User:
        """사용자 생성"""
        try:
            user = User(
                user_id=user_id,
                employee_id=employee_id,
                name=name,
                create_dt=datetime.now(),
                is_active=True
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """사용자 조회 (ID로)"""
        try:
            return self.db.query(User).filter(
                and_(User.user_id == user_id, User.is_deleted == False)
            ).first()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_user_by_employee_id(self, employee_id: str) -> Optional[User]:
        """사용자 조회 (사번으로)"""
        try:
            return self.db.query(User).filter(
                and_(User.employee_id == employee_id, User.is_deleted == False)
            ).first()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_users(self, skip: int = 0, limit: int = 100, is_active: bool = None) -> List[User]:
        """사용자 목록 조회"""
        try:
            query = self.db.query(User).filter(User.is_deleted == False)
            
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            
            return query.order_by(desc(User.create_dt)).offset(skip).limit(limit).all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def search_users(self, keyword: str, skip: int = 0, limit: int = 100) -> List[User]:
        """사용자 검색 (이름 또는 사번으로)"""
        try:
            return self.db.query(User).filter(
                and_(
                    User.is_deleted == False,
                    (User.name.contains(keyword) | User.employee_id.contains(keyword))
                )
            ).order_by(desc(User.create_dt)).offset(skip).limit(limit).all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_user(self, user_id: str, name: str = None, employee_id: str = None) -> Optional[User]:
        """사용자 정보 수정"""
        try:
            user = self.get_user(user_id)
            if user:
                if name is not None:
                    user.name = name
                if employee_id is not None:
                    # 사번 중복 체크
                    existing_user = self.get_user_by_employee_id(employee_id)
                    if existing_user and existing_user.user_id != user_id:
                        raise HandledException(
                            ResponseCode.USER_ALREADY_EXISTS,
                            msg=f"사번 {employee_id}는 이미 사용 중입니다."
                        )
                    user.employee_id = employee_id
                
                user.update_dt = datetime.now()
                self.db.commit()
                self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def deactivate_user(self, user_id: str) -> bool:
        """사용자 비활성화 (소프트 삭제)"""
        try:
            user = self.get_user(user_id)
            if user:
                user.is_active = False
                user.update_dt = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def activate_user(self, user_id: str) -> bool:
        """사용자 활성화"""
        try:
            user = self.get_user(user_id)
            if user:
                user.is_active = True
                user.update_dt = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def delete_user(self, user_id: str) -> bool:
        """사용자 삭제 (하드 삭제)"""
        try:
            user = self.get_user(user_id)
            if user:
                user.is_deleted = True
                user.update_dt = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_user_count(self, is_active: bool = None) -> int:
        """사용자 수 조회"""
        try:
            query = self.db.query(User).filter(User.is_deleted == False)
            
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            
            return query.count()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def check_employee_id_exists(self, employee_id: str, exclude_user_id: str = None) -> bool:
        """사번 중복 체크"""
        try:
            query = self.db.query(User).filter(
                and_(User.employee_id == employee_id, User.is_deleted == False)
            )
            
            if exclude_user_id:
                query = query.filter(User.user_id != exclude_user_id)
            
            return query.first() is not None
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
