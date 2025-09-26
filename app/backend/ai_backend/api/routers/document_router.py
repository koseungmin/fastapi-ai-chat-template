# _*_ coding: utf-8 _*_
"""Document Management API endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
import io
import logging
import os
from pathlib import Path

from ai_backend.core.dependencies import get_document_service
from ai_backend.api.services.document_service import DocumentService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["document-management"])


@router.post("/upload")
def upload_document_request(
    file: UploadFile = File(...),
    user_id: str = Form(default="user"),
    is_public: bool = Form(default=False),
    permissions: Optional[str] = Form(default=None),  # JSON 문자열로 권한 리스트 전달
    document_type: str = Form(default="common"),  # common, type1, type2
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 업로드 요청"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    
    # 권한 파라미터 처리 (JSON 문자열을 리스트로 변환)
    parsed_permissions = None
    if permissions:
        try:
            import json
            parsed_permissions = json.loads(permissions)
        except (json.JSONDecodeError, TypeError):
            return {
                "status": "error",
                "message": "권한 파라미터가 올바른 JSON 형식이 아닙니다."
            }
    
    result = document_service.upload_document(
        file=file,
        user_id=user_id,
        is_public=is_public,
        permissions=parsed_permissions,
        document_type=document_type
    )
    return {
        "status": "success",
        "message": "문서가 업로드되었습니다.",
        "data": result
    }


@router.post("/upload-folder")
def upload_folder(
    folder_path: str = Form(...),
    user_id: str = Form(default="user"),
    is_public: bool = Form(default=False),
    document_service: DocumentService = Depends(get_document_service)
):
    """폴더 전체 업로드 (Document 테이블에 저장)"""
    try:
        import os
        from pathlib import Path
        from fastapi import UploadFile
        from io import BytesIO
        
        # 폴더 경로 검증
        if not folder_path or not os.path.exists(folder_path):
            return {
                "status": "error",
                "message": "폴더 경로가 존재하지 않습니다."
            }
        
        if not os.path.isdir(folder_path):
            return {
                "status": "error", 
                "message": "입력한 경로가 폴더가 아닙니다."
            }
        
        # 폴더 내 파일들 찾기
        folder_path_obj = Path(folder_path)
        allowed_extensions = {'.pdf', '.txt', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.xls', '.xlsx', '.log'}
        
        files_to_upload = []
        for file_path in folder_path_obj.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
                files_to_upload.append(file_path)
        
        if not files_to_upload:
            return {
                "status": "error",
                "message": "업로드 가능한 파일이 없습니다."
            }
        
        # 각 파일을 업로드 (기존 upload_document 호출)
        uploaded_count = 0
        failed_count = 0
        failed_files = []
        uploaded_documents = []
        
        for file_path in files_to_upload:
            try:
                # 파일을 UploadFile 객체로 변환
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # UploadFile 객체 생성
                file_obj = UploadFile(
                    filename=file_path.name,
                    file=BytesIO(file_content),
                    size=len(file_content)
                )
                
                # 기존 upload_document 호출
                result = document_service.upload_document(
                    file=file_obj,
                    user_id=user_id,
                    is_public=is_public
                )
                
                uploaded_documents.append(result)
                uploaded_count += 1
                logger.info(f"파일 업로드 성공: {file_path.name}")
                
            except Exception as e:
                failed_count += 1
                failed_files.append(file_path.name)
                logger.error(f"파일 업로드 실패: {file_path.name}, 오류: {e}")
        
        return {
            "status": "success",
            "message": f"폴더 업로드 완료: {uploaded_count}개 성공, {failed_count}개 실패",
            "uploaded_count": uploaded_count,
            "failed_count": failed_count,
            "failed_files": failed_files,
            "uploaded_documents": uploaded_documents
        }
        
    except Exception as e:
        logger.error(f"폴더 업로드 중 오류: {e}")
        return {
            "status": "error",
            "message": f"폴더 업로드 중 오류가 발생했습니다: {str(e)}"
        }




@router.get("/documents")
def get_documents(
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 목록 조회"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    documents = document_service.get_user_documents(user_id)
    return {
        "status": "success",
        "data": documents
    }


@router.get("/documents/{document_id}")
def get_document(
    document_id: str,
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 정보 조회"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    document = document_service.get_document(document_id, user_id)
    return {
        "status": "success",
        "data": document
    }


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: str,
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 다운로드"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    file_content, filename, media_type = document_service.download_document(
        document_id, user_id
    )
    
    # 한글 파일명 처리를 위한 URL 인코딩
    import urllib.parse
    encoded_filename = urllib.parse.quote(filename.encode('utf-8'))
    
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )


@router.get("/search")
def search_documents(
    search_term: str = Query(...),
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 검색"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    documents = document_service.search_documents(user_id, search_term)
    return {
        "status": "success",
        "data": documents
    }


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 삭제"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = document_service.delete_document(document_id, user_id)
    if success:
        return {
            "status": "success",
            "message": "문서가 삭제되었습니다."
        }
    else:
        return {
            "status": "error",
            "message": "문서 삭제에 실패했습니다."
        }




@router.get("/stats")
def get_document_stats(
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 통계 조회 (기본 통계)"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    # 전체 문서 수
    all_documents = document_service.get_user_documents(user_id)
    total_documents = len(all_documents)
    
    
    # 파일 타입별 통계
    file_types = {}
    total_size = 0
    
    for doc in all_documents:
        file_type = doc["file_type"]
        file_size = doc["file_size"]
        
        if file_type not in file_types:
            file_types[file_type] = {"count": 0, "total_size": 0}
        
        file_types[file_type]["count"] += 1
        file_types[file_type]["total_size"] += file_size
        total_size += file_size
    
    return {
        "status": "success",
        "data": {
            "total_documents": total_documents,
            "total_size": total_size,
            "file_type_stats": file_types
        }
    }


@router.get("/processing-stats")
def get_processing_stats(
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 처리 통계 조회 (처리 상태, 페이지, 벡터 등)"""
    stats = document_service.get_document_processing_stats(user_id)
    return {
        "status": "success",
        "data": stats
    }


@router.put("/documents/{document_id}/processing")
def update_document_processing(
    document_id: str,
    status: str = Form(...),
    user_id: str = Form(default="user"),
    total_pages: Optional[int] = Form(None),
    processed_pages: Optional[int] = Form(None),
    vector_count: Optional[int] = Form(None),
    milvus_collection_name: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 처리 상태 및 메타데이터 업데이트"""
    # 업데이트할 처리 정보 구성
    processing_info = {}
    if total_pages is not None:
        processing_info['total_pages'] = total_pages
    if processed_pages is not None:
        processing_info['processed_pages'] = processed_pages
    if vector_count is not None:
        processing_info['vector_count'] = vector_count
    if milvus_collection_name is not None:
        processing_info['milvus_collection_name'] = milvus_collection_name
    if language is not None:
        processing_info['language'] = language
    if author is not None:
        processing_info['author'] = author
    if subject is not None:
        processing_info['subject'] = subject
    
    success = document_service.update_document_processing_status(
        document_id=document_id,
        user_id=user_id,
        status=status,
        **processing_info
    )
    
    if success:
        return {
            "status": "success",
            "message": "문서 처리 정보가 업데이트되었습니다."
        }
    else:
        return {
            "status": "error",
            "message": "문서 처리 정보 업데이트에 실패했습니다."
        }


@router.get("/upload/{upload_id}/status")
def get_upload_status(
    upload_id: str,
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """업로드 상태 조회"""
    # upload_id는 실제로는 document_id입니다
    document = document_service.get_document(upload_id, user_id)
    return {
        "status": "success",
        "data": {
            "document_id": upload_id,
            "status": document.get("status", "unknown"),
            "error": document.get("error_message") if document.get("status") == "failed" else None
        }
    }


@router.get("/documents/{document_id}/permissions")
def get_document_permissions(
    document_id: str,
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 권한 조회"""
    document = document_service.get_document(document_id, user_id)
    return {
        "status": "success",
        "data": {
            "document_id": document_id,
            "permissions": document.get("permissions", [])
        }
    }


@router.put("/documents/{document_id}/permissions")
def update_document_permissions(
    document_id: str,
    user_id: str = Form(default="user"),
    permissions: str = Form(...),  # JSON 문자열로 권한 리스트 전달
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 권한 전체 업데이트"""
    # 권한 파라미터 처리
    try:
        import json
        parsed_permissions = json.loads(permissions)
        if not isinstance(parsed_permissions, list):
            return {
                "status": "error",
                "message": "권한은 문자열 배열이어야 합니다."
            }
    except (json.JSONDecodeError, TypeError):
        return {
            "status": "error",
            "message": "권한 파라미터가 올바른 JSON 형식이 아닙니다."
        }
    
    success = document_service.update_document_permissions(
        document_id=document_id,
        user_id=user_id,
        permissions=parsed_permissions
    )
    
    if success:
        return {
            "status": "success",
            "message": "문서 권한이 업데이트되었습니다."
        }
    else:
        return {
            "status": "error",
            "message": "문서 권한 업데이트에 실패했습니다."
        }


@router.post("/documents/{document_id}/permissions/{permission}")
def add_document_permission(
    document_id: str,
    permission: str,
    user_id: str = Form(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서에 권한 추가"""
    success = document_service.add_document_permission(
        document_id=document_id,
        user_id=user_id,
        permission=permission
    )
    
    if success:
        return {
            "status": "success",
            "message": f"'{permission}' 권한이 추가되었습니다."
        }
    else:
        return {
            "status": "error",
            "message": "권한 추가에 실패했습니다."
        }


@router.delete("/documents/{document_id}/permissions/{permission}")
def remove_document_permission(
    document_id: str,
    permission: str,
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서에서 권한 제거"""
    success = document_service.remove_document_permission(
        document_id=document_id,
        user_id=user_id,
        permission=permission
    )
    
    if success:
        return {
            "status": "success",
            "message": f"'{permission}' 권한이 제거되었습니다."
        }
    else:
        return {
            "status": "error",
            "message": "권한 제거에 실패했습니다."
        }


@router.get("/documents/permissions/{permission}")
def get_documents_with_permission(
    permission: str,
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """특정 권한을 가진 문서 목록 조회"""
    documents = document_service.get_documents_with_permission(user_id, permission)
    return {
        "status": "success",
        "data": documents
    }


@router.post("/documents/{document_id}/check-permission")
def check_document_permission(
    document_id: str,
    user_id: str = Form(default="user"),
    permission: str = Form(...),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 특정 권한 체크"""
    has_permission = document_service.check_document_permission(
        document_id=document_id,
        user_id=user_id,
        required_permission=permission
    )
    
    return {
        "status": "success",
        "data": {
            "document_id": document_id,
            "permission": permission,
            "has_permission": has_permission
        }
    }


@router.post("/documents/{document_id}/check-permissions")
def check_document_permissions(
    document_id: str,
    user_id: str = Form(default="user"),
    permissions: str = Form(...),  # JSON 문자열로 권한 리스트 전달
    require_all: bool = Form(default=False),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 여러 권한 체크"""
    # 권한 파라미터 처리
    try:
        import json
        parsed_permissions = json.loads(permissions)
        if not isinstance(parsed_permissions, list):
            return {
                "status": "error",
                "message": "권한은 문자열 배열이어야 합니다."
            }
    except (json.JSONDecodeError, TypeError):
        return {
            "status": "error",
            "message": "권한 파라미터가 올바른 JSON 형식이 아닙니다."
        }
    
    has_permissions = document_service.check_document_permissions(
        document_id=document_id,
        user_id=user_id,
        required_permissions=parsed_permissions,
        require_all=require_all
    )
    
    return {
        "status": "success",
        "data": {
            "document_id": document_id,
            "permissions": parsed_permissions,
            "require_all": require_all,
            "has_permissions": has_permissions
        }
    }


@router.get("/documents/types/{document_type}")
def get_documents_by_type(
    document_type: str,
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """특정 타입의 문서 목록 조회"""
    documents = document_service.get_documents_by_type(user_id, document_type)
    return {
        "status": "success",
        "data": documents
    }


@router.put("/documents/{document_id}/type")
def update_document_type(
    document_id: str,
    user_id: str = Form(default="user"),
    document_type: str = Form(...),  # common, type1, type2
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 타입 업데이트"""
    success = document_service.update_document_type(
        document_id=document_id,
        user_id=user_id,
        document_type=document_type
    )
    
    if success:
        return {
            "status": "success",
            "message": f"문서 타입이 '{document_type}'으로 업데이트되었습니다."
        }
    else:
        return {
            "status": "error",
            "message": "문서 타입 업데이트에 실패했습니다."
        }


@router.get("/document-type-stats")
def get_document_type_stats(
    user_id: str = Query(default="user"),
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 타입별 통계 조회"""
    stats = document_service.get_document_type_stats(user_id)
    return {
        "status": "success",
        "data": {
            "type_statistics": stats,
            "total_documents": sum(stats.values()),
            "available_types": ["common", "type1", "type2"]
        }
    }




