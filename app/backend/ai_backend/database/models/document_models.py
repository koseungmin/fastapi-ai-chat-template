# _*_ coding: utf-8 _*_
from sqlalchemy import Column, Text, String, DateTime, Boolean, Integer, ForeignKey, LargeBinary
from sqlalchemy.sql.expression import func, false, true
from ai_backend.database.base import Base

__all__ = [
    "Document",
    "DocumentFolder",
    "DocumentUpload",
]

class DocumentFolder(Base):
    __tablename__ = "DOCUMENT_FOLDERS"
    
    folder_id = Column('FOLDER_ID', String(50), primary_key=True)
    folder_name = Column('FOLDER_NAME', String(100), nullable=False)
    parent_folder_id = Column('PARENT_FOLDER_ID', String(50), ForeignKey('DOCUMENT_FOLDERS.FOLDER_ID'), nullable=True)
    user_id = Column('USER_ID', String(50), nullable=False)
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    is_active = Column('IS_ACTIVE', Boolean, nullable=False, server_default=true())

class Document(Base):
    __tablename__ = "DOCUMENTS"
    
    document_id = Column('DOCUMENT_ID', String(50), primary_key=True)
    document_name = Column('DOCUMENT_NAME', String(255), nullable=False)
    original_filename = Column('ORIGINAL_FILENAME', String(255), nullable=False)
    file_key = Column('FILE_KEY', String(255), nullable=False)  # 파일 시스템 경로 또는 S3 키
    file_size = Column('FILE_SIZE', Integer, nullable=False)  # 바이트 단위
    file_type = Column('FILE_TYPE', String(100), nullable=False)  # MIME 타입
    file_extension = Column('FILE_EXTENSION', String(10), nullable=False)  # 확장자
    folder_id = Column('FOLDER_ID', String(50), ForeignKey('DOCUMENT_FOLDERS.FOLDER_ID'), nullable=True)
    user_id = Column('USER_ID', String(50), nullable=False)
    upload_path = Column('UPLOAD_PATH', String(500), nullable=False)  # 실제 파일 경로
    is_public = Column('IS_PUBLIC', Boolean, nullable=False, server_default=false())
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    is_deleted = Column('IS_DELETED', Boolean, nullable=False, server_default=false())


class DocumentUpload(Base):
    """문서 업로드 상태 관리 테이블"""
    __tablename__ = "DOCUMENT_UPLOADS"
    
    upload_id = Column('UPLOAD_ID', String(50), primary_key=True)
    user_id = Column('USER_ID', String(50), nullable=False)
    folder_id = Column('FOLDER_ID', String(50), ForeignKey('DOCUMENT_FOLDERS.FOLDER_ID'), nullable=True)
    original_filename = Column('ORIGINAL_FILENAME', String(255), nullable=False)
    file_size = Column('FILE_SIZE', Integer, nullable=True)  # 업로드 중에는 null
    file_type = Column('FILE_TYPE', String(50), nullable=True)  # 업로드 중에는 null
    file_extension = Column('FILE_EXTENSION', String(10), nullable=True)  # 업로드 중에는 null
    is_public = Column('IS_PUBLIC', Boolean, nullable=False, server_default=false())
    status = Column('STATUS', String(20), nullable=False)  # processing, completed, failed
    error_message = Column('ERROR_MESSAGE', Text, nullable=True)  # 실패 시 에러 메시지
    result_data = Column('RESULT_DATA', Text, nullable=True)  # 완료 시 결과 데이터 (JSON)
    start_time = Column('START_TIME', DateTime, nullable=False, server_default=func.now())
    end_time = Column('END_TIME', DateTime, nullable=True)  # 완료/실패 시점
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    update_dt = Column('UPDATE_DT', DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
