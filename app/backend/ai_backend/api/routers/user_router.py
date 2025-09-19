# _*_ coding: utf-8 _*_
"""User REST API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from ai_backend.core.dependencies import get_user_service
from ai_backend.api.services.user_service import UserService
from ai_backend.types.request.user_request import (
    CreateUserRequest, 
    UpdateUserRequest, 
    UserSearchRequest, 
    UserListRequest
)
from ai_backend.types.response.user_response import (
    UserResponse, 
    UserListResponse, 
    UserSearchResponse,
    UserCreateResponse,
    UserUpdateResponse,
    UserStatusResponse,
    UserDeleteResponse,
    UserCountResponse,
    UserExistsResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["user"])




@router.post("/users", response_model=UserCreateResponse)
def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(get_user_service)
):
    """새로운 사용자를 생성합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    user = user_service.create_user(
        user_id=request.user_id,
        employee_id=request.employee_id,
        name=request.name
    )
    
    return UserCreateResponse(
        user_id=user.user_id,
        employee_id=user.employee_id,
        name=user.name
    )


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 ID로 사용자 정보를 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    user = user_service.get_user(user_id)
    return UserResponse.from_orm(user)


@router.get("/users/employee/{employee_id}", response_model=UserResponse)
def get_user_by_employee_id(
    employee_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사번으로 사용자 정보를 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    user = user_service.get_user_by_employee_id(employee_id)
    return UserResponse.from_orm(user)


@router.get("/users", response_model=UserListResponse)
def get_users(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    is_active: bool = Query(None, description="활성 상태 필터"),
    user_service: UserService = Depends(get_user_service)
):
    """사용자 목록을 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    users, total_count = user_service.get_users(skip, limit, is_active)
    
    return UserListResponse(
        users=[UserResponse.from_orm(user) for user in users],
        total_count=total_count,
            skip=skip,
            limit=limit
        )


@router.get("/users/search", response_model=UserSearchResponse)
def search_users(
    keyword: str = Query(..., min_length=1, max_length=100, description="검색 키워드"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    user_service: UserService = Depends(get_user_service)
):
    """사용자를 검색합니다 (이름 또는 사번으로)."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    users = user_service.search_users(keyword, skip, limit)
    
    return UserSearchResponse(
        users=[UserResponse.from_orm(user) for user in users],
        keyword=keyword,
        total_count=len(users),
        skip=skip,
        limit=limit
    )


@router.put("/users/{user_id}", response_model=UserUpdateResponse)
def update_user(
    user_id: str,
    request: UpdateUserRequest,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 정보를 수정합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    user = user_service.update_user(
        user_id=user_id,
        name=request.name,
        employee_id=request.employee_id
    )
    
    return UserUpdateResponse(user_id=user_id)


@router.patch("/users/{user_id}/deactivate", response_model=UserStatusResponse)
def deactivate_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자를 비활성화합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = user_service.deactivate_user(user_id)
    
    return UserStatusResponse(
        user_id=user_id,
        is_active=False,
        message="사용자가 비활성화되었습니다."
    )


@router.patch("/users/{user_id}/activate", response_model=UserStatusResponse)
def activate_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자를 활성화합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = user_service.activate_user(user_id)
    
    return UserStatusResponse(
        user_id=user_id,
        is_active=True,
        message="사용자가 활성화되었습니다."
    )


@router.delete("/users/{user_id}", response_model=UserDeleteResponse)
def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자를 삭제합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = user_service.delete_user(user_id)
    
    return UserDeleteResponse(user_id=user_id)


@router.get("/users/stats/count", response_model=UserCountResponse)
def get_user_count(
    is_active: bool = Query(None, description="활성 상태 필터"),
    user_service: UserService = Depends(get_user_service)
):
    """사용자 수를 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    if is_active is not None:
        count = user_service.get_user_count(is_active)
        return UserCountResponse(
            total_count=count,
            active_count=count if is_active else 0,
            inactive_count=0 if is_active else count
        )
    else:
        stats = user_service.get_user_statistics()
        return UserCountResponse(**stats)


@router.get("/users/check/exists", response_model=UserExistsResponse)
def check_user_exists(
    user_id: str = Query(None, description="사용자 ID"),
    employee_id: str = Query(None, description="사번"),
    user_service: UserService = Depends(get_user_service)
):
    """사용자 존재 여부를 확인합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    if not user_id and not employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id 또는 employee_id 중 하나는 필수입니다."
        )
    
    user = None
    if user_id:
        user = user_service.get_user(user_id)
    elif employee_id:
        user = user_service.get_user_by_employee_id(employee_id)
    
    return UserExistsResponse(
        exists=user is not None,
        user_id=user.user_id if user else None,
        employee_id=user.employee_id if user else None
    )


