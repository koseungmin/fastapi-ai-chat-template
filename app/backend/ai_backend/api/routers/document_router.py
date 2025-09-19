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
    document_service: DocumentService = Depends(get_document_service)
):
    """문서 업로드 요청"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    result = document_service.upload_document(
        file=file,
        user_id=user_id,
        is_public=is_public
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
    
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
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
    """문서 통계 조회"""
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




