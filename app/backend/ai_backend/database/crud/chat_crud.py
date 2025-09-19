# _*_ coding: utf-8 _*_
"""Chat CRUD operations with database."""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime
from ai_backend.database.models.chat_models import Chat, ChatMessage
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode

logger = logging.getLogger(__name__)


class ChatCRUD:
    """Chat 관련 CRUD 작업을 처리하는 클래스 - DB 기반"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_chat(self, chat_id: str, chat_title: str, user_id: str) -> Chat:
        """채팅 생성"""
        try:
            chat = Chat(
                chat_id=chat_id,
                chat_title=chat_title,
                user_id=user_id,
                create_dt=datetime.now(),
                is_active=True  # 활성 상태로 생성
            )
            self.session.add(chat)
            self.session.commit()
            self.session.refresh(chat)
            return chat
        except Exception as e:
            logger.error(f"Database error creating chat: {str(e)}")
            self.session.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def create_message(
        self, 
        message_id: str, 
        chat_id: str, 
        user_id: str, 
        message: str, 
        message_type: str = "text",
        status: str = None,
        is_cancelled: bool = False
    ) -> ChatMessage:
        """메시지 생성"""
        try:
            chat_message = ChatMessage(
                message_id=message_id,
                chat_id=chat_id,
                user_id=user_id,
                message=message,
                message_type=message_type,
                status=status,
                is_cancelled=is_cancelled,
                create_dt=datetime.now()
            )
            self.session.add(chat_message)
            self.session.commit()
            self.session.refresh(chat_message)
            
            # 채팅의 마지막 메시지 시간 업데이트
            self.update_chat_last_message(chat_id)
            
            return chat_message
        except Exception as e:
            logger.error(f"Database error creating message: {str(e)}")
            self.session.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_messages(self, chat_id: str, limit: int = 50) -> List[ChatMessage]:
        """특정 채팅의 메시지 조회"""
        try:
            return self.session.query(ChatMessage)\
                .filter(ChatMessage.chat_id == chat_id)\
                .filter(ChatMessage.is_deleted == False)\
                .order_by(ChatMessage.create_dt)\
                .limit(limit)\
                .all()
        except Exception as e:
            log_error("Database error getting messages", e)
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_chat(self, chat_id: str) -> Optional[Chat]:
        """채팅 조회"""
        try:
            return self.session.query(Chat).filter(Chat.chat_id == chat_id).first()
        except Exception as e:
            log_error("Database error getting chat", e)
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_chat_or_create(self, chat_id: str, user_id: str = "user") -> Chat:
        """채팅이 없으면 생성하고 반환"""
        try:
            chat = self.get_chat(chat_id)
            if not chat:
                chat = self.create_chat(
                    chat_id=chat_id,
                    chat_title=f"Chat {chat_id}",
                    user_id=user_id
                )
            return chat
        except Exception as e:
            logger.error(f"Database error in get_chat_or_create: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def save_user_message(self, message_id: str, chat_id: str, user_id: str, message: str) -> ChatMessage:
        """사용자 메시지 저장"""
        try:
            return self.create_message(
                message_id=message_id,
                chat_id=chat_id,
                user_id=user_id,
                message=message,
                message_type="user",
                status="completed"
            )
        except Exception as e:
            logger.error(f"Database error saving user message: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def save_ai_message(self, message_id: str, chat_id: str, user_id: str, message: str, status: str = "completed") -> ChatMessage:
        """AI 메시지 저장"""
        try:
            return self.create_message(
                message_id=message_id,
                chat_id=chat_id,
                user_id=user_id,
                message=message,
                message_type="assistant",
                status=status
            )
        except Exception as e:
            logger.error(f"Database error saving AI message: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_messages_from_db(self, chat_id: str) -> List[dict]:
        """데이터베이스에서 메시지 조회하여 딕셔너리로 변환"""
        try:
            messages = self.get_messages(chat_id)
            
            # ChatMessage 객체를 딕셔너리로 변환
            history = []
            for msg in messages:
                role = "user" if msg.message_type == "user" else "assistant"
                if msg.is_cancelled:
                    role = "system"
                
                history.append({
                    "role": role,
                    "content": msg.message,
                    "timestamp": msg.create_dt.isoformat(),
                    "cancelled": msg.is_cancelled
                })
            
            # 시간순으로 정렬 (오래된 것부터)
            history.sort(key=lambda x: x["timestamp"])
            return history
        except Exception as e:
            logger.error(f"Database error getting messages: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def clear_conversation(self, chat_id: str):
        """대화 기록 초기화 (DB에서 메시지 삭제)"""
        try:
            # 채팅의 모든 메시지를 삭제 상태로 변경
            messages = self.get_messages(chat_id)
            for msg in messages:
                msg.is_deleted = True
            self.session.commit()
        except Exception as e:
            logger.error(f"Database error clearing conversation: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_message_to_error(self, message_id: str, error_message: str):
        """메시지를 에러 상태로 업데이트"""
        try:
            self.update_message_status(message_id, "error")
            # 에러 메시지로 업데이트
            message = self.session.query(ChatMessage).filter(ChatMessage.message_id == message_id).first()
            if message:
                message.message = f"❌ 오류가 발생했습니다: {error_message}"
                self.session.commit()
        except Exception as e:
            logger.error(f"Database error updating message to error: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_active_generating_chats(self) -> List[dict]:
        """현재 생성 중인 채팅 목록 반환"""
        try:
            # status가 'generating'인 메시지가 있는 채팅들을 직접 조회
            active_chats = []
            # generating 상태인 메시지들을 조회
            generating_messages = self.session.query(ChatMessage)\
                .filter(ChatMessage.status == "generating")\
                .filter(ChatMessage.is_deleted == False)\
                .all()
            
            # 채팅 ID별로 그룹화
            chat_ids = set(msg.chat_id for msg in generating_messages)
            for chat_id in chat_ids:
                chat = self.get_chat(chat_id)
                if chat:
                    active_chats.append({
                        "chat_id": chat_id,
                        "chat_title": chat.chat_title,
                        "user_id": chat.user_id,
                        "created_at": chat.create_dt.isoformat()
                    })
            
            return active_chats
        except Exception as e:
            logger.error(f"Database error getting active generating chats: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def save_user_message_simple(self, message_id: str, chat_id: str, user_id: str, message: str):
        """사용자 메시지 저장"""
        try:
            self.create_message(
                message_id=message_id,
                chat_id=chat_id,
                user_id=user_id,
                message=message,
                message_type="user",
                status="completed"
            )
        except Exception as e:
            logger.error(f"Database error saving user message: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def save_ai_message_generating(self, message_id: str, chat_id: str, user_id: str):
        """AI 메시지를 generating 상태로 저장"""
        try:
            self.create_message(
                message_id=message_id,
                chat_id=chat_id,
                user_id=user_id,
                message="",  # 빈 메시지로 시작
                message_type="assistant",
                status="generating"
            )
        except Exception as e:
            logger.error(f"Database error saving AI message generating: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_ai_message_completed(self, message_id: str, content: str):
        """AI 메시지를 완료 상태로 업데이트"""
        try:
            self.update_message_status(message_id, "completed")
            # 메시지 내용도 업데이트
            message = self.session.query(ChatMessage).filter(ChatMessage.message_id == message_id).first()
            if message:
                message.message = content
                self.session.commit()
        except Exception as e:
            logger.error(f"Database error updating AI message completed: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_user_chats(self, user_id: str) -> List[Chat]:
        """사용자의 채팅 목록 조회"""
        try:
            return self.session.query(Chat)\
                .filter(Chat.user_id == user_id)\
                .filter(Chat.is_active == True)\
                .order_by(desc(Chat.create_dt))\
                .all()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_chat_last_message(self, chat_id: str):
        """채팅의 마지막 메시지 시간 업데이트"""
        try:
            chat = self.get_chat(chat_id)
            if chat:
                chat.last_message_at = datetime.now()
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_message_status(self, message_id: str, status: str, is_cancelled: bool = False):
        """메시지 상태 업데이트"""
        try:
            message = self.session.query(ChatMessage).filter(ChatMessage.message_id == message_id).first()
            if message:
                message.status = status
                message.is_cancelled = is_cancelled
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def delete_message(self, message_id: str) -> bool:
        """메시지 삭제 (소프트 삭제)"""
        try:
            message = self.session.query(ChatMessage).filter(ChatMessage.message_id == message_id).first()
            if message:
                message.is_deleted = True
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def delete_chat(self, chat_id: str) -> bool:
        """채팅 삭제 (소프트 삭제)"""
        try:
            chat = self.session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if chat:
                chat.is_active = False
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
