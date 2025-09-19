# _*_ coding: utf-8 _*_
"""Document CRUD operations with database."""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
from ai_backend.database.models.document_models import Document, DocumentFolder, DocumentUpload
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode

logger = logging.getLogger(__name__)


class DocumentCRUD:
    """Document 관련 CRUD 작업을 처리하는 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_folder(self, folder_id: str, folder_name: str, user_id: str, parent_folder_id: str = None) -> DocumentFolder:
        """폴더 생성"""
        try:
            folder = DocumentFolder(
                folder_id=folder_id,
                folder_name=folder_name,
                parent_folder_id=parent_folder_id,
                user_id=user_id,
                create_dt=datetime.now(),
                is_active=True
            )
            self.db.add(folder)
            self.db.commit()
            self.db.refresh(folder)
            return folder
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_folder(self, folder_id: str) -> Optional[DocumentFolder]:
        """폴더 조회"""
        try:
            return self.db.query(DocumentFolder).filter(DocumentFolder.folder_id == folder_id).first()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_user_folders(self, user_id: str, parent_folder_id: str = None) -> List[DocumentFolder]:
        """사용자의 폴더 목록 조회"""
        try:
            query = self.db.query(DocumentFolder)\
                .filter(DocumentFolder.user_id == user_id)\
                .filter(DocumentFolder.is_active == True)
            
            if parent_folder_id is None:
                query = query.filter(DocumentFolder.parent_folder_id.is_(None))
            else:
                query = query.filter(DocumentFolder.parent_folder_id == parent_folder_id)
            
            return query.order_by(desc(DocumentFolder.create_dt)).all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
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
        folder_id: str = None,
        is_public: bool = False
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
                folder_id=folder_id,
                user_id=user_id,
                upload_path=upload_path,
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
    
    def get_user_documents(self, user_id: str, folder_id: str = None) -> List[Document]:
        """사용자의 문서 목록 조회"""
        try:
            query = self.db.query(Document)\
                .filter(Document.user_id == user_id)\
                .filter(Document.is_deleted == False)
            
            if folder_id:
                query = query.filter(Document.folder_id == folder_id)
            else:
                query = query.filter(Document.folder_id.is_(None))
            
            return query.order_by(desc(Document.create_dt)).all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_documents_by_folder(self, folder_id: str) -> List[Document]:
        """특정 폴더의 문서 목록 조회"""
        try:
            return self.db.query(Document)\
                .filter(Document.folder_id == folder_id)\
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
    
    def delete_folder(self, folder_id: str) -> bool:
        """폴더 삭제 (소프트 삭제)"""
        try:
            folder = self.get_folder(folder_id)
            if folder:
                folder.is_active = False
                # 폴더 내 모든 문서도 삭제
                documents = self.get_documents_by_folder(folder_id)
                for doc in documents:
                    doc.is_deleted = True
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_folder_tree(self, user_id: str, parent_folder_id: str = None) -> List[dict]:
        """폴더 트리 구조 조회"""
        try:
            folders = self.get_user_folders(user_id, parent_folder_id)
            result = []
            
            for folder in folders:
                folder_data = {
                    "folder_id": folder.folder_id,
                    "folder_name": folder.folder_name,
                    "parent_folder_id": folder.parent_folder_id,
                    "create_dt": folder.create_dt.isoformat(),
                    "sub_folders": self.get_folder_tree(user_id, folder.folder_id),
                    "document_count": len(self.get_documents_by_folder(folder.folder_id))
                }
                result.append(folder_data)
            
            return result
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    # ==========================================
    # 업로드 상태 관리 메서드들
    # ==========================================
    
    def create_upload(self, upload_id: str, user_id: str, original_filename: str, 
                     folder_id: str = None, is_public: bool = False) -> bool:
        """업로드 상태 생성"""
        try:
            upload = DocumentUpload(
                upload_id=upload_id,
                user_id=user_id,
                folder_id=folder_id,
                original_filename=original_filename,
                is_public=is_public,
                status="processing"
            )
            self.db.add(upload)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_upload_status(self, upload_id: str, status: str, 
                           error_message: str = None, result_data: Dict = None) -> bool:
        """업로드 상태 업데이트"""
        try:
            upload = self.db.query(DocumentUpload).filter(
                DocumentUpload.upload_id == upload_id
            ).first()
            
            if not upload:
                return False
            
            upload.status = status
            upload.error_message = error_message
            
            if result_data:
                upload.result_data = json.dumps(result_data, ensure_ascii=False)
                # 결과 데이터에서 파일 정보 추출
                if 'file_size' in result_data:
                    upload.file_size = result_data['file_size']
                if 'file_type' in result_data:
                    upload.file_type = result_data['file_type']
                if 'file_extension' in result_data:
                    upload.file_extension = result_data['file_extension']
            
            if status in ["completed", "failed"]:
                upload.end_time = datetime.now()
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_upload_status(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """업로드 상태 조회"""
        try:
            upload = self.db.query(DocumentUpload).filter(
                DocumentUpload.upload_id == upload_id
            ).first()
            
            if not upload:
                return None
            
            result = {
                "upload_id": upload.upload_id,
                "user_id": upload.user_id,
                "folder_id": upload.folder_id,
                "original_filename": upload.original_filename,
                "file_size": upload.file_size,
                "file_type": upload.file_type,
                "file_extension": upload.file_extension,
                "is_public": upload.is_public,
                "status": upload.status,
                "error_message": upload.error_message,
                "start_time": upload.start_time.isoformat() if upload.start_time else None,
                "end_time": upload.end_time.isoformat() if upload.end_time else None,
                "create_dt": upload.create_dt.isoformat() if upload.create_dt else None,
                "update_dt": upload.update_dt.isoformat() if upload.update_dt else None
            }
            
            # 처리 시간 계산
            if upload.start_time:
                if upload.end_time:
                    result["processing_time"] = (upload.end_time - upload.start_time).total_seconds()
                else:
                    result["processing_time"] = (datetime.now() - upload.start_time).total_seconds()
            
            # 결과 데이터 파싱
            if upload.result_data:
                try:
                    result["result_data"] = json.loads(upload.result_data)
                except json.JSONDecodeError:
                    result["result_data"] = None
            
            return result
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_upload_result(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """업로드 결과 조회 (완료된 경우만)"""
        try:
            upload = self.db.query(DocumentUpload).filter(
                DocumentUpload.upload_id == upload_id
            ).first()
            
            if not upload:
                return None
            
            if upload.status == "processing":
                return {"status": "processing", "message": "아직 처리 중입니다."}
            elif upload.status == "failed":
                return {"status": "failed", "message": upload.error_message}
            elif upload.status == "completed":
                if upload.result_data:
                    return json.loads(upload.result_data)
                else:
                    return {"status": "completed", "message": "처리 완료"}
            else:
                return {"status": "unknown", "message": "알 수 없는 상태입니다."}
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def delete_upload(self, upload_id: str) -> bool:
        """업로드 상태 삭제 (완료 후 정리용)"""
        try:
            upload = self.db.query(DocumentUpload).filter(
                DocumentUpload.upload_id == upload_id
            ).first()
            
            if not upload:
                return False
            
            self.db.delete(upload)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def cleanup_old_uploads(self, days: int = 7) -> int:
        """오래된 업로드 상태 정리"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            deleted_count = self.db.query(DocumentUpload).filter(
                DocumentUpload.create_dt < cutoff_date,
                DocumentUpload.status.in_(["completed", "failed"])
            ).delete()
            
            self.db.commit()
            return deleted_count
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
