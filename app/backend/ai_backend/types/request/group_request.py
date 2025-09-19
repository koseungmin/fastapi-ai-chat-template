# _*_ coding: utf-8 _*_
"""Group request models."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CreateGroupRequest(BaseModel):
    """그룹 생성 요청"""
    group_name: str = Field(..., min_length=1, max_length=100, description="그룹명")
    description: Optional[str] = Field(None, max_length=500, description="그룹 설명")
    owner_id: str = Field(..., min_length=1, max_length=50, description="그룹 소유자 ID")
    max_members: Optional[int] = Field(None, ge=1, le=1000, description="최대 멤버 수")
    
    @field_validator('group_name')
    @classmethod
    def validate_group_name(cls, v):
        if not v.strip():
            raise ValueError('그룹명은 공백일 수 없습니다.')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('그룹 설명은 공백일 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('owner_id')
    @classmethod
    def validate_owner_id(cls, v):
        if not v.strip():
            raise ValueError('그룹 소유자 ID는 공백일 수 없습니다.')
        return v.strip()


class UpdateGroupRequest(BaseModel):
    """그룹 수정 요청"""
    group_name: Optional[str] = Field(None, min_length=1, max_length=100, description="그룹명")
    description: Optional[str] = Field(None, max_length=500, description="그룹 설명")
    max_members: Optional[int] = Field(None, ge=1, le=1000, description="최대 멤버 수")
    
    @field_validator('group_name')
    @classmethod
    def validate_group_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('그룹명은 공백일 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('그룹 설명은 공백일 수 없습니다.')
        return v.strip() if v else v


class GroupSearchRequest(BaseModel):
    """그룹 검색 요청"""
    keyword: str = Field(..., min_length=1, max_length=100, description="검색 키워드 (그룹명)")
    skip: int = Field(0, ge=0, description="건너뛸 개수")
    limit: int = Field(100, ge=1, le=1000, description="조회할 개수")
    
    @field_validator('keyword')
    @classmethod
    def validate_keyword(cls, v):
        if not v.strip():
            raise ValueError('검색 키워드는 공백일 수 없습니다.')
        return v.strip()


class GroupListRequest(BaseModel):
    """그룹 목록 조회 요청"""
    skip: int = Field(0, ge=0, description="건너뛸 개수")
    limit: int = Field(100, ge=1, le=1000, description="조회할 개수")
    is_active: Optional[bool] = Field(None, description="활성 상태 필터")
    owner_id: Optional[str] = Field(None, description="소유자 ID 필터")


class AddMemberRequest(BaseModel):
    """그룹 멤버 추가 요청"""
    user_id: str = Field(..., min_length=1, max_length=50, description="사용자 ID")
    role: str = Field('member', description="멤버 역할")
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('사용자 ID는 공백일 수 없습니다.')
        return v.strip()
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        valid_roles = ['owner', 'admin', 'member']
        if v not in valid_roles:
            raise ValueError(f'유효한 역할은 {valid_roles} 중 하나여야 합니다.')
        return v


class UpdateMemberRoleRequest(BaseModel):
    """그룹 멤버 역할 변경 요청"""
    role: str = Field(..., description="새로운 멤버 역할")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        valid_roles = ['owner', 'admin', 'member']
        if v not in valid_roles:
            raise ValueError(f'유효한 역할은 {valid_roles} 중 하나여야 합니다.')
        return v
