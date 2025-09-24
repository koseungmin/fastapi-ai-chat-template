# _*_ coding: utf-8 _*_
"""LLM Chat REST API endpoints (Redis 기반, 확장 가능)."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from ai_backend.core.dependencies import get_llm_chat_service
from ai_backend.api.services.llm_chat_service import LLMChatService
from ai_backend.types.request.chat_request import UserMessageRequest, ClearConversationRequest, CreateChatRequest
from pydantic import BaseModel
from ai_backend.types.response.chat_response import AIResponse, ConversationHistoryResponse, ConversationClearedResponse, ErrorResponse, CreateChatResponse, ChatListResponse
from ai_backend.types.response.exceptions import HandledException
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(tags=["llm-chat"])

class GenerateTitleRequest(BaseModel):
    message: str

@router.post("/chat/{chat_id}/message", response_model=AIResponse)
def send_message(
    chat_id: str,
    request: UserMessageRequest,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """사용자 메시지를 전송하고 AI 응답을 받습니다."""
    logger.info(f"Received message for chat {chat_id}: {request.message[:50]}...")
    
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    ai_response = llm_chat_service.send_message_simple(
        chat_id, 
        request.message, 
        request.user_id
    )
    
    return AIResponse(
        message_id=ai_response["message_id"],
        content=ai_response["content"],
        user_id="ai",
        timestamp=ai_response["timestamp"]
    )

@router.post("/chat/{chat_id}/stream")
async def send_message_stream(
    chat_id: str,
    request: UserMessageRequest,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """스트리밍 방식으로 메시지를 전송하고 AI 응답을 받습니다 (SSE)."""

    async def generate_stream():
        try:
            # 사용자 메시지 저장
            user_message_id = llm_chat_service.save_user_message(
                chat_id, request.message, request.user_id
            )

            # 사용자 메시지 스트림 전송
            yield f"data: {json.dumps({'type': 'user_message', 'message_id': user_message_id, 'content': request.message, 'user_id': request.user_id, 'timestamp': llm_chat_service.get_current_timestamp()}, ensure_ascii=False)}\n\n"

            # AI 응답 생성 (스트리밍)
            async for chunk in llm_chat_service.generate_ai_response_stream(chat_id, request.user_id):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        except HandledException as e:
            # HandledException은 스트림으로 전달 (연결 유지)
            logger.error(f"HandledException in streaming: {str(e)}")
            from ai_backend.types.response.chat_response import StreamErrorResponse
            error_response = StreamErrorResponse(
                code=e.code,
                message=e.message,
                content=f"메시지 처리 중 오류가 발생했습니다: {e.message}",
                timestamp=llm_chat_service.get_current_timestamp(),
                chat_id=chat_id
            )
            yield f"data: {json.dumps(error_response.dict(), ensure_ascii=False)}\n\n"
        except Exception as e:
            # 예상치 못한 예외도 스트림으로 전달 (연결 유지)
            logger.error(f"Unexpected error in streaming: {str(e)}")
            from ai_backend.types.response.chat_response import StreamErrorResponse
            error_response = StreamErrorResponse(
                code=-2,  # UNDEFINED_ERROR
                message='정의되지 않은 오류입니다.',
                content=f"메시지 처리 중 예상치 못한 오류가 발생했습니다: {str(e)}",
                timestamp=llm_chat_service.get_current_timestamp(),
                chat_id=chat_id
            )
            yield f"data: {json.dumps(error_response.dict(), ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.get("/chat/{chat_id}/history", response_model=ConversationHistoryResponse)
def get_conversation_history(
    chat_id: str,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """대화 기록을 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    history = llm_chat_service.get_conversation_history(chat_id)
    return ConversationHistoryResponse(history=history)

@router.post("/chat/{chat_id}/clear", response_model=ConversationClearedResponse)
def clear_conversation(
    chat_id: str,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """대화 기록을 초기화합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    llm_chat_service.clear_conversation(chat_id)
    return ConversationClearedResponse(message="대화 기록이 초기화되었습니다.")

@router.post("/chat/{chat_id}/cancel")
async def cancel_generation(
    chat_id: str,
    user_id: str = "user",
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """현재 생성 중인 AI 응답을 취소합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = await llm_chat_service.cancel_generation(chat_id, user_id)
    if success:
        return {"message": "AI 응답 생성이 취소되었습니다.", "cancelled": True}
    else:
        return {"message": "취소할 수 있는 생성이 없습니다.", "cancelled": False}

@router.post("/chat/chats", response_model=CreateChatResponse)
def create_chat(
    request: CreateChatRequest,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """새로운 채팅을 생성합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    chat_id = llm_chat_service.create_chat(request.chat_title, request.user_id)
    chat_info = llm_chat_service.get_chat_info(chat_id)
    
    return CreateChatResponse(
        chat_id=chat_id,
        chat_title=request.chat_title,
        user_id=request.user_id,
        created_at=chat_info["created_at"]
    )


@router.get("/chat/chats", response_model=ChatListResponse)
def get_chats(
    user_id: str,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """사용자의 채팅 목록을 조회합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    chats = llm_chat_service.get_user_chats(user_id)
    return ChatListResponse(chats=chats)


@router.delete("/chat/chats/{chat_id}")
def delete_chat(
    chat_id: str,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """채팅을 삭제합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = llm_chat_service.delete_chat(chat_id)
    if success:
        return {"message": "채팅이 삭제되었습니다.", "deleted": True}
    else:
        return {"message": "채팅 삭제에 실패했습니다.", "deleted": False}


@router.put("/chat/chats/{chat_id}/title")
def update_chat_title(
    chat_id: str,
    new_title: str,
    user_id: str,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """채팅방 이름을 변경합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    success = llm_chat_service.update_chat_title(chat_id, new_title, user_id)
    if success:
        return {"message": "채팅방 이름이 변경되었습니다.", "success": True}
    else:
        return {"message": "채팅방 이름 변경에 실패했습니다.", "success": False}


@router.post("/chat/generate-title")
async def generate_chat_title(
    request: GenerateTitleRequest,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """메시지를 기반으로 채팅방 제목을 생성합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    title = await llm_chat_service.generate_chat_title(request.message)
    return {"title": title}



