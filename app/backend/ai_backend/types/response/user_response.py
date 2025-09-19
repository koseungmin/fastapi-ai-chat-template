# _*_ coding: utf-8 _*_
"""User response models."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserResponse(BaseModel):
    """사용자 응답"""
    user_id: str
    employee_id: str
    name: str
    create_dt: datetime
    update_dt: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """사용자 목록 응답"""
    users: List[UserResponse]
    total_count: int
    skip: int
    limit: int


class UserSearchResponse(BaseModel):
    """사용자 검색 응답"""
    users: List[UserResponse]
    keyword: str
    total_count: int
    skip: int
    limit: int


class UserCreateResponse(BaseModel):
    """사용자 생성 응답"""
    user_id: str
    employee_id: str
    name: str
    message: str = "사용자가 성공적으로 생성되었습니다."


class UserUpdateResponse(BaseModel):
    """사용자 수정 응답"""
    user_id: str
    message: str = "사용자 정보가 성공적으로 수정되었습니다."


class UserStatusResponse(BaseModel):
    """사용자 상태 변경 응답"""
    user_id: str
    is_active: bool
    message: str


class UserDeleteResponse(BaseModel):
    """사용자 삭제 응답"""
    user_id: str
    message: str = "사용자가 성공적으로 삭제되었습니다."


class UserCountResponse(BaseModel):
    """사용자 수 응답"""
    total_count: int
    active_count: int
    inactive_count: int


class UserExistsResponse(BaseModel):
    """사용자 존재 여부 응답"""
    exists: bool
    user_id: Optional[str] = None
    employee_id: Optional[str] = None
