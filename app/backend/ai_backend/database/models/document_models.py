# _*_ coding: utf-8 _*_
from sqlalchemy import Column, Text, String, DateTime, Boolean, Integer, ForeignKey, LargeBinary
from sqlalchemy.sql.expression import func, false, true
from ai_backend.database.base import Base

__all__ = [
    "Document",
]

class Document(Base):
    __tablename__ = "DOCUMENTS"
    
    document_id = Column('DOCUMENT_ID', String(50), primary_key=True)
    document_name = Column('DOCUMENT_NAME', String(255), nullable=False)
    original_filename = Column('ORIGINAL_FILENAME', String(255), nullable=False)
    file_key = Column('FILE_KEY', String(255), nullable=False)  # 파일 시스템 경로 또는 S3 키
    file_size = Column('FILE_SIZE', Integer, nullable=False)  # 바이트 단위
    file_type = Column('FILE_TYPE', String(100), nullable=False)  # MIME 타입
    file_extension = Column('FILE_EXTENSION', String(10), nullable=False)  # 확장자
    user_id = Column('USER_ID', String(50), nullable=False)
    upload_path = Column('UPLOAD_PATH', String(500), nullable=False)  # 실제 파일 경로
    status = Column('STATUS', String(20), nullable=False, server_default='completed')  # processing, completed, failed
    error_message = Column('ERROR_MESSAGE', Text, nullable=True)  # 실패 시 에러 메시지
    is_public = Column('IS_PUBLIC', Boolean, nullable=False, server_default=false())
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    is_deleted = Column('IS_DELETED', Boolean, nullable=False, server_default=false())
