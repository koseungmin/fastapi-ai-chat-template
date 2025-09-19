# _*_ coding: utf-8 _*_
"""Document Service for handling file uploads and management."""
import os
import uuid
import mimetypes
import logging
import threading
import time
from typing import Dict, List, Optional, BinaryIO
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session
from ai_backend.database.crud.document_crud import DocumentCRUD
from ai_backend.database.models.document_models import Document
from ai_backend.utils.uuid_gen import gen
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode
from ai_backend.config.simple_settings import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """문서 관리 서비스"""
    
    def __init__(self, db: Session, upload_base_path: str = None):
        self.db = db
        # 환경변수에서 업로드 경로 가져오기 (k8s 환경 대응)
        self.upload_base_path = Path(upload_base_path or settings.upload_base_path)
        self.upload_base_path.mkdir(parents=True, exist_ok=True)
        self.document_crud = DocumentCRUD(db)
    
    def _get_file_extension(self, filename: str) -> str:
        """파일 확장자 추출"""
        return Path(filename).suffix.lower()
    
    def _get_mime_type(self, filename: str) -> str:
        """MIME 타입 추출"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    def _generate_file_key(self, user_id: str, filename: str = None) -> str:
        """파일 키 생성 (저장 경로)"""
        # 폴더 구조: uploads/user_id/filename
        return f"{user_id}/{filename}"
    
    def _get_upload_path(self, file_key: str) -> Path:
        """실제 업로드 경로 생성"""
        return self.upload_base_path / file_key
    
    
    def upload_document(
        self,
        file: UploadFile,
        user_id: str,
        is_public: bool = False
    ) -> Dict:
        """문서 업로드"""
        try:
            # 파일 정보 추출
            original_filename = file.filename
            file_extension = self._get_file_extension(original_filename)
            file_type = self._get_mime_type(original_filename)
            
            # 파일 크기 확인 (환경변수에서 설정값 가져오기)
            file_content = file.file.read()
            file_size = len(file_content)
            max_size = settings.upload_max_size
            
            if file_size > max_size:
                max_size_mb = settings.get_upload_max_size_mb()
                raise HandledException(ResponseCode.DOCUMENT_FILE_TOO_LARGE, 
                                     msg=f"파일 크기가 너무 큽니다. (최대 {max_size_mb:.1f}MB)")
            
            # 허용된 파일 타입 확인 (환경변수에서 설정값 가져오기)
            allowed_extensions = settings.get_upload_allowed_types()
            file_extension_lower = file_extension.lstrip('.')
            
            if file_extension_lower not in allowed_extensions:
                allowed_types_str = ', '.join(allowed_extensions)
                raise HandledException(ResponseCode.DOCUMENT_INVALID_FILE_TYPE, 
                                     msg=f"지원하지 않는 파일 형식입니다. 허용된 형식: {allowed_types_str}")
            
            # 파일 저장
            document_id = gen()
            file_key = self._generate_file_key(user_id, original_filename)
            upload_path = self._get_upload_path(file_key)
            
            # 디렉토리 생성
            upload_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 저장
            with open(upload_path, "wb") as f:
                f.write(file_content)
            
            # DB에 메타데이터 저장
            document = self.document_crud.create_document(
                document_id=document_id,
                document_name=original_filename,
                original_filename=original_filename,
                file_key=file_key,
                file_size=file_size,
                file_type=file_type,
                file_extension=file_extension,
                user_id=user_id,
                upload_path=str(upload_path),
                is_public=is_public
            )
            
            return {
                "document_id": document.document_id,
                "document_name": document.document_name,
                "file_size": document.file_size,
                "file_type": document.file_type,
                "file_extension": document.file_extension,
                "upload_path": document.upload_path,
                "is_public": document.is_public,
                "create_dt": document.create_dt.isoformat()
            }
                
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.DOCUMENT_UPLOAD_ERROR, e=e)
    
    def get_document(self, document_id: str, user_id: str) -> Dict:
        """문서 정보 조회"""
        try:
            # DocumentCRUD 사용
                document = self.document_crud.get_document(document_id)
                
                if not document or document.user_id != user_id or document.is_deleted:
                    raise HandledException(ResponseCode.DOCUMENT_NOT_FOUND, msg="문서를 찾을 수 없습니다.")
                
                return {
                    "document_id": document.document_id,
                    "document_name": document.document_name,
                    "original_filename": document.original_filename,
                    "file_size": document.file_size,
                    "file_type": document.file_type,
                    "file_extension": document.file_extension,
                    "folder_id": document.folder_id,
                    "is_public": document.is_public,
                    "create_dt": document.create_dt.isoformat()
                }
                
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_user_documents(self, user_id: str) -> List[Dict]:
        """사용자의 문서 목록 조회"""
        try:
            # DocumentCRUD 사용
            documents = self.document_crud.get_user_documents(user_id)
            
            return [
                {
                    "document_id": doc.document_id,
                    "document_name": doc.document_name,
                    "file_size": doc.file_size,
                    "file_type": doc.file_type,
                    "file_extension": doc.file_extension,
                    "is_public": doc.is_public,
                    "create_dt": doc.create_dt.isoformat()
                }
                for doc in documents
            ]
                
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    
    def search_documents(self, user_id: str, search_term: str) -> List[Dict]:
        """문서 검색"""
        try:
            # DocumentCRUD 사용
                documents = self.document_crud.search_documents(user_id, search_term)
                
                return [
                    {
                        "document_id": doc.document_id,
                        "document_name": doc.document_name,
                        "file_size": doc.file_size,
                        "file_type": doc.file_type,
                        "file_extension": doc.file_extension,
                        "is_public": doc.is_public,
                        "create_dt": doc.create_dt.isoformat()
                    }
                    for doc in documents
                ]
                
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def download_document(self, document_id: str, user_id: str) -> tuple[bytes, str, str]:
        """문서 다운로드"""
        try:
            # DocumentCRUD 사용
                document = self.document_crud.get_document(document_id)
                
                if not document or document.user_id != user_id or document.is_deleted:
                    raise HandledException(ResponseCode.DOCUMENT_NOT_FOUND, msg="문서를 찾을 수 없습니다.")
                
                # 파일 읽기
                upload_path = Path(document.upload_path)
                if not upload_path.exists():
                    raise HandledException(ResponseCode.DOCUMENT_NOT_FOUND, msg="파일이 존재하지 않습니다.")
                
                with open(upload_path, "rb") as f:
                    file_content = f.read()
                
                return file_content, document.original_filename, document.file_type
                
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.DOCUMENT_DOWNLOAD_ERROR, e=e)
    
    def delete_document(self, document_id: str, user_id: str) -> bool:
        """문서 삭제"""
        try:
            # DocumentCRUD 사용
                document = self.document_crud.get_document(document_id)
                
                if not document or document.user_id != user_id:
                    raise HandledException(ResponseCode.DOCUMENT_NOT_FOUND, msg="문서를 찾을 수 없습니다.")
                
                # DB에서 소프트 삭제
                success = self.document_crud.delete_document(document_id)
                
                # 실제 파일도 삭제
                if success:
                    upload_path = Path(document.upload_path)
                    if upload_path.exists():
                        upload_path.unlink()
                
                return success
                
        except HandledException:
            raise  # HandledException은 그대로 전파
        except Exception as e:
            raise HandledException(ResponseCode.DOCUMENT_DELETE_ERROR, e=e)
    
    
