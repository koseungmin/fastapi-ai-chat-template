# _*_ coding: utf-8 _*_
"""Document CRUD operations with database."""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
from ai_backend.database.models.document_models import Document
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode

logger = logging.getLogger(__name__)


class DocumentCRUD:
    """Document 관련 CRUD 작업을 처리하는 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_document(
        self,
        document_id: str,
        document_name: str,
        original_filename: str,
        file_key: str,
        file_size: int,
        file_type: str,
        file_extension: str,
        user_id: str,
        upload_path: str,
        is_public: bool = False,
        status: str = 'completed',
        error_message: str = None
    ) -> Document:
        """문서 생성"""
        try:
            document = Document(
                document_id=document_id,
                document_name=document_name,
                original_filename=original_filename,
                file_key=file_key,
                file_size=file_size,
                file_type=file_type,
                file_extension=file_extension,
                user_id=user_id,
                upload_path=upload_path,
                status=status,
                error_message=error_message,
                is_public=is_public,
                create_dt=datetime.now()
            )
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            return document
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """문서 조회"""
        try:
            return self.db.query(Document).filter(Document.document_id == document_id).first()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_user_documents(self, user_id: str) -> List[Document]:
        """사용자의 문서 목록 조회"""
        try:
            return self.db.query(Document)\
                .filter(Document.user_id == user_id)\
                .filter(Document.is_deleted == False)\
                .order_by(desc(Document.create_dt))\
                .all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    
    def search_documents(self, user_id: str, search_term: str) -> List[Document]:
        """문서 검색"""
        try:
            return self.db.query(Document)\
                .filter(Document.user_id == user_id)\
                .filter(Document.is_deleted == False)\
                .filter(
                    (Document.document_name.contains(search_term)) |
                    (Document.original_filename.contains(search_term))
                )\
                .order_by(desc(Document.create_dt))\
                .all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_document(self, document_id: str, **kwargs) -> bool:
        """문서 정보 업데이트"""
        try:
            document = self.get_document(document_id)
            if document:
                for key, value in kwargs.items():
                    if hasattr(document, key):
                        setattr(document, key, value)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_document_status(self, document_id: str, status: str, error_message: str = None) -> bool:
        """문서 상태 업데이트"""
        try:
            document = self.get_document(document_id)
            if document:
                document.status = status
                if error_message:
                    document.error_message = error_message
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def delete_document(self, document_id: str) -> bool:
        """문서 삭제 (소프트 삭제)"""
        try:
            document = self.get_document(document_id)
            if document:
                document.is_deleted = True
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
