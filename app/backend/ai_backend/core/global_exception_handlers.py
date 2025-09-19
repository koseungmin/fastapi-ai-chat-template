# _*_ coding: utf-8 _*_
"""Global exception handlers for FastAPI application."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError as HTTPRequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK
import datetime as dt
import uuid
import logging
import redis.exceptions

# from autologging import traced, logged
from ..types.response.exceptions import (
    HandledException,
    UnHandledException,
)
from ..types.response.chat_response import ErrorResponse, StreamErrorResponse
from ..utils.logging_utils import log_error

logger = logging.getLogger(__name__)


def create_error_response(
    code: int,
    message: str,
    content: str = None,
    trace_id: str = None,
    http_status_code: int = 400
) -> ErrorResponse:
    """에러 응답 생성"""
    if content is None:
        content = message
    
    return ErrorResponse(
        code=code,
        message=message,
        content=content,
        timestamp=dt.datetime.utcnow().isoformat(),
        trace_id=trace_id or str(uuid.uuid4())
    )


def create_stream_error_response(
    code: int,
    message: str,
    content: str = None,
    chat_id: str = None
) -> StreamErrorResponse:
    """스트리밍 에러 응답 생성"""
    if content is None:
        content = message
    
    return StreamErrorResponse(
        code=code,
        message=message,
        content=content,
        timestamp=dt.datetime.utcnow().isoformat(),
        chat_id=chat_id
    )


async def handled_exception_handler(request: Request, exc: HandledException) -> JSONResponse:
    """HandledException 처리"""
    error_response = create_error_response(
        code=exc.code,
        message=exc.message,
        content=f"요청 처리 중 오류가 발생했습니다: {exc.message}",
        http_status_code=exc.http_status_code
    )
    
    return JSONResponse(
        status_code=exc.http_status_code,
        content=jsonable_encoder(error_response)
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """예상치 못한 예외 처리"""
    trace_id = str(uuid.uuid4())
    
    # UnHandledException으로 래핑
    managed_exc = UnHandledException(e=exc)
    
    error_response = create_error_response(
        code=managed_exc.code,
        message=managed_exc.message,
        content="서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        trace_id=trace_id,
        http_status_code=500
    )
    
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(error_response)
    )


async def http_exception_handler_wrapper(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP 예외 처리"""
    error_response = create_error_response(
        code=exc.status_code,
        message=exc.detail,
        content=f"HTTP 오류가 발생했습니다: {exc.detail}",
        http_status_code=exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_response)
    )


async def validation_exception_handler(request: Request, exc: HTTPRequestValidationError) -> JSONResponse:
    """요청 검증 예외 처리"""
    error_response = create_error_response(
        code=422,
        message="요청 데이터가 유효하지 않습니다.",
        content="입력한 데이터를 확인해주세요.",
        http_status_code=422
    )
    
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(error_response)
    )


def get_request_info(request: Request) -> str:
    """요청 정보 문자열 생성"""
    return "\n".join([
        "=" * 50,
        "Request",
        f"{{method: {request.method}}}",
        f"{{url: {request.url}}}",
        f"{{headers: {request.headers}}}",
        f"{{client: {request.client}}}",
        "=" * 50,
    ])


def set_global_exception_handlers(app: FastAPI) -> FastAPI:
    """글로벌 예외 핸들러 설정"""

    @app.exception_handler(HandledException)
    async def handeled_exception_handler(request, exc):
        # HandledException 로깅 (환경변수로 exc_info 제어)
        try:
            from ai_backend.config.simple_settings import settings
            from ai_backend.utils.logging_utils import log_error
            
            log_msg = f"HandledException [{exc.code}]: {exc.message}\nRequest: {get_request_info(request)}"
            log_error(log_msg, exc)
        except Exception:
            # 로깅 실패 시 기본 로깅
            logger.error(
                f"HandledException [{exc.code}]: {exc.message}\n"
                f"Request: {get_request_info(request)}",
                exc_info=True
            )
        
        return await handled_exception_handler(request, exc)

    @app.exception_handler(UnHandledException)
    async def unhandled_exception_handler_wrapper(request, exc):
        log_msg = f"UnHandledException [{exc.code}]: {exc.message}\nRequest: {get_request_info(request)}\nOriginal exception: {exc.logMessage}"
        log_error(log_msg, exc)
        return await unhandled_exception_handler(request, exc)

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request, exc):
        log_msg = f"HTTPException [{exc.status_code}]: {exc.detail}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await http_exception_handler_wrapper(request, exc)

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request, exc):
        log_msg = f"StarletteHTTPException [{exc.status_code}]: {exc.detail}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await http_exception_handler_wrapper(request, exc)

    @app.exception_handler(HTTPRequestValidationError)
    async def validation_exception_handler_wrapper(request, exc):
        log_msg = f"ValidationError: {exc.errors()}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await validation_exception_handler(request, exc)

    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        log_msg = f"ValueError: {str(exc)}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await unhandled_exception_handler(request, exc)

    @app.exception_handler(KeyError)
    async def key_error_handler(request, exc):
        log_msg = f"KeyError: {str(exc)}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await unhandled_exception_handler(request, exc)

    @app.exception_handler(ConnectionError)
    async def connection_error_handler(request, exc):
        log_msg = f"ConnectionError: {str(exc)}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await unhandled_exception_handler(request, exc)

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_error_handler(request, exc):
        log_msg = f"FileNotFoundError: {str(exc)}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await unhandled_exception_handler(request, exc)

    @app.exception_handler(redis.exceptions.ResponseError)
    async def redis_response_error_handler(request, exc):
        log_msg = f"Redis ResponseError: {str(exc)}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await unhandled_exception_handler(request, exc)

    @app.exception_handler(redis.exceptions.ConnectionError)
    async def redis_connection_error_handler(request, exc):
        log_msg = f"Redis ConnectionError: {str(exc)}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await unhandled_exception_handler(request, exc)

    @app.exception_handler(redis.exceptions.TimeoutError)
    async def redis_timeout_error_handler(request, exc):
        log_msg = f"Redis TimeoutError: {str(exc)}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await unhandled_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        log_msg = f"Unexpected exception [{exc.__class__.__name__}]: {str(exc)}\nRequest: {get_request_info(request)}"
        log_error(log_msg, exc)
        return await unhandled_exception_handler(request, exc)

    return app