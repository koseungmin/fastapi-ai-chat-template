# _*_ coding: utf-8 _*_
"""Group REST API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from ai_backend.core.dependencies import get_group_service
from ai_backend.api.services.group_service import GroupService
from ai_backend.types.request.group_request import (
    CreateGroupRequest, 
    UpdateGroupRequest, 
    GroupSearchRequest, 
    GroupListRequest,
    AddMemberRequest,
    UpdateMemberRoleRequest
)
from ai_backend.types.response.group_response import (
    GroupResponse, 
    GroupListResponse, 
    GroupSearchResponse,
    GroupCreateResponse,
    GroupUpdateResponse,
    GroupStatusResponse,
    GroupDeleteResponse,
    GroupCountResponse,
    GroupExistsResponse,
    GroupDetailResponse,
    GroupMemberListResponse,
    GroupMemberAddResponse,
    GroupMemberRemoveResponse,
    GroupMemberRoleUpdateResponse,
    GroupMemberResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["group"])


@router.post("/groups", response_model=GroupCreateResponse)
def create_group(
    request: CreateGroupRequest,
    group_service: GroupService = Depends(get_group_service)
):
    """새로운 그룹을 생성합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    group = group_service.create_group(
        group_name=request.group_name,
        description=request.description,
        owner_id=request.owner_id,
        max_members=request.max_members
    )
    
    return GroupCreateResponse(
        group_id=group.group_id,
        group_name=group.group_name,
        owner_id=group.owner_id
    )


@router.get("/groups/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: str,
    group_service: GroupService = Depends(get_group_service)
):
    """그룹 ID로 그룹 정보를 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    group = group_service.get_group(group_id)
    
    # 멤버 수 추가
    member_count = group_service.member_crud.get_group_member_count(group_id)
    group_response = GroupResponse.from_orm(group)
    group_response.member_count = member_count
    
    return group_response


@router.get("/groups/name/{group_name}", response_model=GroupResponse)
def get_group_by_name(
    group_name: str,
    group_service: GroupService = Depends(get_group_service)
):
    """그룹명으로 그룹 정보를 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    group = group_service.get_group_by_name(group_name)
    
    # 멤버 수 추가
    member_count = group_service.member_crud.get_group_member_count(group.group_id)
    group_response = GroupResponse.from_orm(group)
    group_response.member_count = member_count
    
    return group_response


@router.get("/groups", response_model=GroupListResponse)
def get_groups(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    is_active: bool = Query(None, description="활성 상태 필터"),
    owner_id: str = Query(None, description="소유자 ID 필터"),
    group_service: GroupService = Depends(get_group_service)
):
    """그룹 목록을 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    groups, total_count = group_service.get_groups(skip, limit, is_active, owner_id)
    
    # 각 그룹에 멤버 수 추가
    group_responses = []
    for group in groups:
        member_count = group_service.member_crud.get_group_member_count(group.group_id)
        group_response = GroupResponse.from_orm(group)
        group_response.member_count = member_count
        group_responses.append(group_response)
    
    return GroupListResponse(
        groups=group_responses,
        total_count=total_count,
        skip=skip,
        limit=limit
    )


@router.get("/groups/search", response_model=GroupSearchResponse)
def search_groups(
    keyword: str = Query(..., min_length=1, max_length=100, description="검색 키워드 (그룹명)"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    group_service: GroupService = Depends(get_group_service)
):
    """그룹을 검색합니다 (그룹명으로)."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    groups = group_service.search_groups(keyword, skip, limit)
    
    # 각 그룹에 멤버 수 추가
    group_responses = []
    for group in groups:
        member_count = group_service.member_crud.get_group_member_count(group.group_id)
        group_response = GroupResponse.from_orm(group)
        group_response.member_count = member_count
        group_responses.append(group_response)
    
    return GroupSearchResponse(
        groups=group_responses,
        keyword=keyword,
        total_count=len(groups),
        skip=skip,
        limit=limit
    )


@router.put("/groups/{group_id}", response_model=GroupUpdateResponse)
def update_group(
    group_id: str,
    request: UpdateGroupRequest,
    group_service: GroupService = Depends(get_group_service)
):
    """그룹 정보를 수정합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    group = group_service.update_group(
        group_id=group_id,
        group_name=request.group_name,
        description=request.description,
        max_members=request.max_members
    )
    
    return GroupUpdateResponse(group_id=group_id)


@router.patch("/groups/{group_id}/deactivate", response_model=GroupStatusResponse)
def deactivate_group(
    group_id: str,
    group_service: GroupService = Depends(get_group_service)
):
    """그룹을 비활성화합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = group_service.deactivate_group(group_id)
    
    return GroupStatusResponse(
        group_id=group_id,
        is_active=False,
        message="그룹이 비활성화되었습니다."
    )


@router.patch("/groups/{group_id}/activate", response_model=GroupStatusResponse)
def activate_group(
    group_id: str,
    group_service: GroupService = Depends(get_group_service)
):
    """그룹을 활성화합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = group_service.activate_group(group_id)
    
    return GroupStatusResponse(
        group_id=group_id,
        is_active=True,
        message="그룹이 활성화되었습니다."
    )


@router.delete("/groups/{group_id}", response_model=GroupDeleteResponse)
def delete_group(
    group_id: str,
    group_service: GroupService = Depends(get_group_service)
):
    """그룹을 삭제합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = group_service.delete_group(group_id)
    
    return GroupDeleteResponse(group_id=group_id)


@router.get("/groups/stats/count", response_model=GroupCountResponse)
def get_group_count(
    is_active: bool = Query(None, description="활성 상태 필터"),
    owner_id: str = Query(None, description="소유자 ID 필터"),
    group_service: GroupService = Depends(get_group_service)
):
    """그룹 수를 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    if is_active is not None:
        count = group_service.get_group_count(is_active, owner_id)
        return GroupCountResponse(
            total_count=count,
            active_count=count if is_active else 0,
            inactive_count=0 if is_active else count
        )
    else:
        stats = group_service.get_group_statistics()
        return GroupCountResponse(**stats)


@router.get("/groups/check/exists", response_model=GroupExistsResponse)
def check_group_exists(
    group_name: str = Query(None, description="그룹명"),
    group_service: GroupService = Depends(get_group_service)
):
    """그룹 존재 여부를 확인합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    if not group_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="group_name은 필수입니다."
        )
    
    try:
        group = group_service.get_group_by_name(group_name)
        return GroupExistsResponse(
            exists=True,
            group_id=group.group_id,
            group_name=group.group_name
        )
    except:
        return GroupExistsResponse(
            exists=False,
            group_id=None,
            group_name=group_name
        )


@router.get("/groups/{group_id}/detail", response_model=GroupDetailResponse)
def get_group_detail(
    group_id: str,
    group_service: GroupService = Depends(get_group_service)
):
    """그룹 상세 정보를 조회합니다 (멤버 포함)."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    group, members = group_service.get_group_detail(group_id)
    
    # 그룹 정보에 멤버 수 추가
    group_response = GroupResponse.from_orm(group)
    group_response.member_count = len(members)
    
    return GroupDetailResponse(
        group=group_response,
        members=[GroupMemberResponse.from_orm(member) for member in members],
        member_count=len(members)
    )


# 그룹 멤버 관련 엔드포인트들
@router.post("/groups/{group_id}/members", response_model=GroupMemberAddResponse)
def add_group_member(
    group_id: str,
    request: AddMemberRequest,
    group_service: GroupService = Depends(get_group_service)
):
    """그룹에 멤버를 추가합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    member = group_service.add_group_member(
        group_id=group_id,
        user_id=request.user_id,
        role=request.role
    )
    
    return GroupMemberAddResponse(
        group_id=group_id,
        user_id=request.user_id,
        member_id=member.member_id,
        role=member.role
    )


@router.get("/groups/{group_id}/members", response_model=GroupMemberListResponse)
def get_group_members(
    group_id: str,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    group_service: GroupService = Depends(get_group_service)
):
    """그룹 멤버 목록을 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    members, total_count = group_service.get_group_members(group_id, skip, limit)
    
    return GroupMemberListResponse(
        group_id=group_id,
        members=[GroupMemberResponse.from_orm(member) for member in members],
        total_count=total_count,
        skip=skip,
        limit=limit
    )


@router.get("/users/{user_id}/groups", response_model=GroupMemberListResponse)
def get_user_groups(
    user_id: str,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    group_service: GroupService = Depends(get_group_service)
):
    """사용자가 속한 그룹 목록을 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    members = group_service.get_user_groups(user_id, skip, limit)
    
    return GroupMemberListResponse(
        group_id=None,  # 사용자 그룹 목록이므로 group_id는 None
        members=[GroupMemberResponse.from_orm(member) for member in members],
        total_count=len(members),
        skip=skip,
        limit=limit
    )


@router.put("/groups/{group_id}/members/{user_id}/role", response_model=GroupMemberRoleUpdateResponse)
def update_member_role(
    group_id: str,
    user_id: str,
    request: UpdateMemberRoleRequest,
    group_service: GroupService = Depends(get_group_service)
):
    """그룹 멤버의 역할을 변경합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    member = group_service.update_member_role(
        group_id=group_id,
        user_id=user_id,
        role=request.role
    )
    
    return GroupMemberRoleUpdateResponse(
        group_id=group_id,
        user_id=user_id,
        role=member.role
    )


@router.delete("/groups/{group_id}/members/{user_id}", response_model=GroupMemberRemoveResponse)
def remove_group_member(
    group_id: str,
    user_id: str,
    group_service: GroupService = Depends(get_group_service)
):
    """그룹에서 멤버를 제거합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = group_service.remove_group_member(group_id, user_id)
    
    return GroupMemberRemoveResponse(
        group_id=group_id,
        user_id=user_id
    )
