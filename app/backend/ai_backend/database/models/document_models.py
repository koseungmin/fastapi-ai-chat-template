# _*_ coding: utf-8 _*_
from sqlalchemy import Column, Text, String, DateTime, Boolean, Integer, ForeignKey, LargeBinary, JSON
from sqlalchemy.sql.expression import func, false, true
from ai_backend.database.base import Base
from datetime import datetime

__all__ = [
    "Document",
]

class Document(Base):
    __tablename__ = "DOCUMENTS"
    
    # 기본 정보 (기존 + 통합)
    document_id = Column('DOCUMENT_ID', String(50), primary_key=True)
    document_name = Column('DOCUMENT_NAME', String(255), nullable=False)
    original_filename = Column('ORIGINAL_FILENAME', String(255), nullable=False)
    
    # 파일 정보 (기존)
    file_key = Column('FILE_KEY', String(255), nullable=False)
    file_size = Column('FILE_SIZE', Integer, nullable=False)
    file_type = Column('FILE_TYPE', String(100), nullable=False)  # MIME 타입
    file_extension = Column('FILE_EXTENSION', String(10), nullable=False)
    upload_path = Column('UPLOAD_PATH', String(500), nullable=False)
    file_hash = Column('FILE_HASH', String(64), nullable=True)  # 🆕 중복 방지
    
    # 사용자 정보 (기존)
    user_id = Column('USER_ID', String(50), nullable=False)
    is_public = Column('IS_PUBLIC', Boolean, nullable=False, server_default=false())
    
    # 문서 타입 (🆕)
    document_type = Column('DOCUMENT_TYPE', String(20), nullable=True, default='common')  # common, type1, type2
    
    # 처리 상태 (기존 + 확장)
    status = Column('STATUS', String(20), nullable=False, server_default='processing')
    total_pages = Column('TOTAL_PAGES', Integer, default=0, nullable=True)  # 🆕
    processed_pages = Column('PROCESSED_PAGES', Integer, default=0, nullable=True)  # 🆕
    error_message = Column('ERROR_MESSAGE', Text, nullable=True)
    
    # 벡터화 정보 (🆕)
    milvus_collection_name = Column('MILVUS_COLLECTION_NAME', String(255), nullable=True)
    vector_count = Column('VECTOR_COUNT', Integer, default=0, nullable=True)
    
    # 문서 메타데이터 (🆕)
    language = Column('LANGUAGE', String(10), nullable=True)
    author = Column('AUTHOR', String(255), nullable=True)
    subject = Column('SUBJECT', String(500), nullable=True)
    
    # JSON 필드 (🆕)
    metadata_json = Column('METADATA_JSON', JSON, nullable=True)
    processing_config = Column('PROCESSING_CONFIG', JSON, nullable=True)
    permissions = Column('PERMISSIONS', JSON, nullable=True)  # 권한 리스트 (string array)
    
    # 시간 정보 (기존 + 확장)
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    updated_at = Column('UPDATED_AT', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)  # 🆕
    processed_at = Column('PROCESSED_AT', DateTime, nullable=True)  # 🆕
    
    # 삭제 플래그 (기존)
    is_deleted = Column('IS_DELETED', Boolean, nullable=False, server_default=false())
