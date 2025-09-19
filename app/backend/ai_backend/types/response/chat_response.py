# _*_ coding: utf-8 _*_
"""Chat response models."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    message_id: str = Field(..., description="메시지 ID")
    content: str = Field(..., description="메시지 내용")
    user_id: str = Field(..., description="사용자 ID")
    timestamp: str = Field(..., description="타임스탬프")


class ConnectionEstablishedResponse(BaseModel):
    """연결 성공 응답 모델"""
    type: str = Field(default="connection_established", description="응답 타입")
    message: str = Field(..., description="연결 성공 메시지")
    chat_id: str = Field(..., description="채팅 ID")


class UserMessageResponse(BaseModel):
    """사용자 메시지 응답 모델"""
    type: str = Field(default="user_message", description="응답 타입")
    message_id: str = Field(..., description="메시지 ID")
    content: str = Field(..., description="메시지 내용")
    user_id: str = Field(..., description="사용자 ID")
    timestamp: str = Field(..., description="타임스탬프")


class AIResponse(BaseModel):
    """AI 응답 모델"""
    type: str = Field(default="ai_response", description="응답 타입")
    message_id: str = Field(..., description="메시지 ID")
    content: str = Field(..., description="AI 응답 내용")
    user_id: str = Field(default="ai", description="사용자 ID")
    timestamp: str = Field(..., description="타임스탬프")


class ConversationHistoryResponse(BaseModel):
    """대화 기록 응답 모델"""
    type: str = Field(default="conversation_history", description="응답 타입")
    history: List[Dict[str, Any]] = Field(..., description="대화 기록")


class ConversationClearedResponse(BaseModel):
    """대화 기록 초기화 응답 모델"""
    type: str = Field(default="conversation_cleared", description="응답 타입")
    message: str = Field(..., description="초기화 완료 메시지")


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    type: str = Field(default="error", description="응답 타입")
    code: int = Field(..., description="에러 코드")
    message: str = Field(..., description="에러 메시지")
    content: str = Field(..., description="사용자에게 표시할 에러 내용")
    timestamp: str = Field(..., description="타임스탬프")
    trace_id: Optional[str] = Field(default=None, description="추적 ID")


class StreamErrorResponse(BaseModel):
    """스트리밍 에러 응답 모델"""
    type: str = Field(default="error", description="응답 타입")
    code: int = Field(..., description="에러 코드")
    message: str = Field(..., description="에러 메시지")
    content: str = Field(..., description="사용자에게 표시할 에러 내용")
    timestamp: str = Field(..., description="타임스탬프")
    chat_id: Optional[str] = Field(default=None, description="채팅 ID")


class Chat(BaseModel):
    """채팅 모델"""
    chat_id: str = Field(..., description="채팅 ID")
    chat_title: str = Field(..., description="채팅 제목")
    user_id: str = Field(..., description="사용자 ID")
    created_at: str = Field(..., description="생성 시간")
    last_message_at: Optional[str] = Field(default=None, description="마지막 메시지 시간")


class CreateChatResponse(BaseModel):
    """채팅 생성 응답 모델"""
    chat_id: str = Field(..., description="채팅 ID")
    chat_title: str = Field(..., description="채팅 제목")
    user_id: str = Field(..., description="사용자 ID")
    created_at: str = Field(..., description="생성 시간")


class ChatListResponse(BaseModel):
    """채팅 목록 응답 모델"""
    chats: List[Chat] = Field(..., description="채팅 목록")
