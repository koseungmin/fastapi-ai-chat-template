# _*_ coding: utf-8 _*_
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql.expression import func, true, false
from ai_backend.database.base import Base

__all__ = [
    "User",
]

class User(Base):
    __tablename__ = "USERS"
    
    user_id = Column('USER_ID', String(50), primary_key=True)  # 사용자 ID
    employee_id = Column('EMPLOYEE_ID', String(20), nullable=False, unique=True)  # 사번
    name = Column('NAME', String(100), nullable=False)  # 이름
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())  # 생성일시
    update_dt = Column('UPDATE_DT', DateTime, nullable=True)  # 수정일시
    is_active = Column('IS_ACTIVE', Boolean, nullable=False, server_default=true())  # 활성 상태
    is_deleted = Column('IS_DELETED', Boolean, nullable=False, server_default=false())  # 삭제 여부
