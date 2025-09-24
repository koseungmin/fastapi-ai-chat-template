# _*_ coding: utf-8 _*_
from sqlalchemy import Column, Text, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.sql.expression import func, false, true
from ai_backend.database.base import Base

__all__ = [
    "Chat",
    "ChatMessage",
]


class Chat(Base):
    __tablename__ = "CHATS"

    chat_id = Column('CHAT_ID', String(50), primary_key=True)
    chat_title = Column('CHAT_TITLE', String(100), nullable=False)
    user_id = Column('USER_ID', String(50), nullable=False)
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    last_message_at = Column('LAST_MESSAGE_AT', DateTime, nullable=True)
    is_active = Column('IS_ACTIVE', Boolean, nullable=False, server_default=true())


class ChatMessage(Base):
    __tablename__ = "CHAT_MESSAGES"

    message_id = Column('MESSAGE_ID', String(50), primary_key=True)
    chat_id = Column('CHAT_ID', String(50), ForeignKey('CHATS.CHAT_ID'), nullable=False)
    user_id = Column('USER_ID', String(50), nullable=False)
    message = Column('MESSAGE', Text, nullable=False)
    message_type = Column('MESSAGE_TYPE', String(20), nullable=False)  # text, image, file, assistant, user, cancelled
    status = Column('STATUS', String(20), nullable=True)  # generating, completed, cancelled, error
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    is_deleted = Column('IS_DELETED', Boolean, nullable=False, server_default=false())
    is_cancelled = Column('IS_CANCELLED', Boolean, nullable=False, server_default=false())  # 취소된 메시지 표시 