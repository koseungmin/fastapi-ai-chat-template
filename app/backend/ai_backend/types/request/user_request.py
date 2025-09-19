# _*_ coding: utf-8 _*_
"""User request models."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CreateUserRequest(BaseModel):
    """사용자 생성 요청"""
    user_id: str = Field(..., min_length=1, max_length=50, description="사용자 ID")
    employee_id: str = Field(..., min_length=1, max_length=20, description="사번")
    name: str = Field(..., min_length=1, max_length=100, description="이름")
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('사용자 ID는 공백일 수 없습니다.')
        return v.strip()
    
    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        if not v.strip():
            raise ValueError('사번은 공백일 수 없습니다.')
        return v.strip()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('이름은 공백일 수 없습니다.')
        return v.strip()


class UpdateUserRequest(BaseModel):
    """사용자 수정 요청"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="이름")
    employee_id: Optional[str] = Field(None, min_length=1, max_length=20, description="사번")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('이름은 공백일 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        if v is not None and not v.strip():
            raise ValueError('사번은 공백일 수 없습니다.')
        return v.strip() if v else v


class UserSearchRequest(BaseModel):
    """사용자 검색 요청"""
    keyword: str = Field(..., min_length=1, max_length=100, description="검색 키워드 (이름 또는 사번)")
    skip: int = Field(0, ge=0, description="건너뛸 개수")
    limit: int = Field(100, ge=1, le=1000, description="조회할 개수")
    
    @field_validator('keyword')
    @classmethod
    def validate_keyword(cls, v):
        if not v.strip():
            raise ValueError('검색 키워드는 공백일 수 없습니다.')
        return v.strip()


class UserListRequest(BaseModel):
    """사용자 목록 조회 요청"""
    skip: int = Field(0, ge=0, description="건너뛸 개수")
    limit: int = Field(100, ge=1, le=1000, description="조회할 개수")
    is_active: Optional[bool] = Field(None, description="활성 상태 필터")
