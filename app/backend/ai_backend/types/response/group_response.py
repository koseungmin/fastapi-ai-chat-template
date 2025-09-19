# _*_ coding: utf-8 _*_
"""Group response models."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class GroupMemberResponse(BaseModel):
    """그룹 멤버 응답"""
    member_id: str
    group_id: str
    user_id: str
    role: str
    join_dt: datetime
    update_dt: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    """그룹 응답"""
    group_id: str
    group_name: str
    description: Optional[str]
    owner_id: str
    max_members: Optional[int]
    create_dt: datetime
    update_dt: Optional[datetime]
    is_active: bool
    member_count: Optional[int] = None  # 멤버 수 (선택적)
    
    class Config:
        from_attributes = True


class GroupListResponse(BaseModel):
    """그룹 목록 응답"""
    groups: List[GroupResponse]
    total_count: int
    skip: int
    limit: int


class GroupSearchResponse(BaseModel):
    """그룹 검색 응답"""
    groups: List[GroupResponse]
    keyword: str
    total_count: int
    skip: int
    limit: int


class GroupCreateResponse(BaseModel):
    """그룹 생성 응답"""
    group_id: str
    group_name: str
    owner_id: str
    message: str = "그룹이 성공적으로 생성되었습니다."


class GroupUpdateResponse(BaseModel):
    """그룹 수정 응답"""
    group_id: str
    message: str = "그룹 정보가 성공적으로 수정되었습니다."


class GroupStatusResponse(BaseModel):
    """그룹 상태 변경 응답"""
    group_id: str
    is_active: bool
    message: str


class GroupDeleteResponse(BaseModel):
    """그룹 삭제 응답"""
    group_id: str
    message: str = "그룹이 성공적으로 삭제되었습니다."


class GroupCountResponse(BaseModel):
    """그룹 수 응답"""
    total_count: int
    active_count: int
    inactive_count: int


class GroupExistsResponse(BaseModel):
    """그룹 존재 여부 응답"""
    exists: bool
    group_id: Optional[str] = None
    group_name: Optional[str] = None


class GroupDetailResponse(BaseModel):
    """그룹 상세 정보 응답 (멤버 포함)"""
    group: GroupResponse
    members: List[GroupMemberResponse]
    member_count: int


class GroupMemberListResponse(BaseModel):
    """그룹 멤버 목록 응답"""
    group_id: str
    members: List[GroupMemberResponse]
    total_count: int
    skip: int
    limit: int


class GroupMemberAddResponse(BaseModel):
    """그룹 멤버 추가 응답"""
    group_id: str
    user_id: str
    member_id: str
    role: str
    message: str = "멤버가 성공적으로 추가되었습니다."


class GroupMemberRemoveResponse(BaseModel):
    """그룹 멤버 제거 응답"""
    group_id: str
    user_id: str
    message: str = "멤버가 성공적으로 제거되었습니다."


class GroupMemberRoleUpdateResponse(BaseModel):
    """그룹 멤버 역할 변경 응답"""
    group_id: str
    user_id: str
    role: str
    message: str = "멤버 역할이 성공적으로 변경되었습니다."
