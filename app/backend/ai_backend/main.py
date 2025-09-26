# -*- coding: utf-8 -*-
import os
import logging
import logging.config
import glob
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from ai_backend.config import settings
from ai_backend.core.global_exception_handlers import set_global_exception_handlers

def cleanup_old_logs():
    """
    오래된 로그 파일을 삭제하는 함수
    
    ==========================================
    기능:
    - LOG_RETENTION_DAYS 설정에 따라 오래된 로그 파일 자동 삭제
    - TimedRotatingFileHandler로 생성된 로그 파일들을 날짜 기반으로 정리
    - 파일명 형식: app.log.2025-09-15 (날짜별 로테이션)
    
    동작 방식:
    1. 로그 디렉토리에서 패턴 매칭으로 로그 파일 검색
    2. 파일명에서 날짜 추출 (YYYY-MM-DD 형식)
    3. 현재 날짜 - 보관 기간을 기준으로 삭제 대상 판단
    4. 보관 기간이 지난 파일들을 안전하게 삭제
    
    예시:
    - 현재 날짜: 2025-09-16
    - 보관 기간: 30일
    - 삭제 기준: 2025-08-17 이전 파일들
    - 삭제됨: app.log.2025-08-16, app.log.2025-08-15, ...
    - 보관됨: app.log.2025-08-17, app.log.2025-08-18, ...
    
    안전장치:
    - 현재 로그 파일 (app.log)은 절대 삭제하지 않음
    - 날짜 형식이 맞지 않는 파일은 건너뛰기
    - 파일 삭제 실패 시 경고 로그만 출력하고 계속 진행
    - 전체 프로세스 실패 시에도 애플리케이션 중단 없음
    """
    # 파일 로깅이 비활성화된 경우 실행하지 않음
    if not settings.log_to_file:
        logger.debug("파일 로깅이 비활성화되어 로그 정리를 건너뜁니다")
        return
    
    try:
        # 설정값 가져오기
        log_dir = settings.log_dir
        log_file = settings.log_file
        retention_days = settings.log_retention_days
        
        logger.debug("로그 정리 시작 - 디렉토리: {}, 보관 기간: {}일".format(log_dir, retention_days))
        
        # 로그 파일 패턴 생성 (app.log.2025-09-15 형태)
        # glob 패턴으로 날짜별 로테이션 파일들 검색
        log_pattern = os.path.join(log_dir, "{log_file}.*".format(log_file=log_file))
        log_files = glob.glob(log_pattern)
        
        if not log_files:
            logger.debug("정리할 로그 파일이 없습니다")
            return
        
        # 현재 날짜에서 보관 기간을 뺀 날짜 계산
        # 이 날짜 이전의 파일들이 삭제 대상
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        logger.debug("삭제 기준 날짜: {}".format(cutoff_date.strftime('%Y-%m-%d')))
        
        deleted_count = 0
        skipped_count = 0
        
        for log_file_path in log_files:
            try:
                # 파일명에서 날짜 추출 (app.log.2025-09-15 -> 2025-09-15)
                filename = os.path.basename(log_file_path)
                
                # 현재 로그 파일 (app.log)은 건너뛰기
                if filename == log_file:
                    logger.debug("현재 로그 파일은 보호됩니다: {}".format(filename))
                    continue
                
                # 파일명에 점이 있는 경우 날짜 부분 추출
                if '.' in filename:
                    date_part = filename.split('.')[-1]
                    try:
                        # 날짜 파싱 (YYYY-MM-DD 형식)
                        file_date = datetime.strptime(date_part, '%Y-%m-%d')
                        
                        # 보관 기간이 지난 파일 삭제
                        if file_date < cutoff_date:
                            os.remove(log_file_path)
                            deleted_count += 1
                            logger.debug("오래된 로그 파일 삭제: {} (날짜: {})".format(log_file_path, date_part))
                        else:
                            logger.debug("보관 기간 내 파일 유지: {} (날짜: {})".format(log_file_path, date_part))
                    except ValueError:
                        # 날짜 형식이 맞지 않는 파일은 건너뛰기
                        # (예: app.log.1, app.log.backup 등)
                        skipped_count += 1
                        logger.debug("날짜 형식이 맞지 않아 건너뛰기: {}".format(filename))
                        continue
                else:
                    # 파일명에 점이 없는 경우도 건너뛰기
                    skipped_count += 1
                    logger.debug("예상하지 못한 파일명 형식으로 건너뛰기: {}".format(filename))
                    
            except Exception as e:
                # 개별 파일 삭제 실패 시 경고 로그만 출력하고 계속 진행
                logger.warning("로그 파일 삭제 중 오류: {}, 오류: {}".format(log_file_path, e))
        
        # 정리 결과 로그 출력
        if deleted_count > 0:
            logger.info("오래된 로그 파일 {}개 삭제 완료 (보관 기간: {}일)".format(deleted_count, retention_days))
        else:
            logger.debug("삭제할 오래된 로그 파일이 없습니다")
            
        if skipped_count > 0:
            logger.debug("날짜 형식이 맞지 않아 건너뛴 파일: {}개".format(skipped_count))
            
    except Exception as e:
        # 전체 프로세스 실패 시에도 애플리케이션 중단 없이 에러 로그만 출력
        logger.error("로그 정리 중 오류 발생: {}".format(e))
        logger.error("로그 정리 실패로 인해 디스크 공간이 부족할 수 있습니다. 수동으로 확인해주세요.")

def setup_logging():
    """ConfigMap 환경변수 기반 동적 로깅 설정"""
    
    # 환경변수에서 로그 레벨 가져오기
    app_log_level = getattr(logging, settings.app_log_level.upper(), logging.INFO)
    server_log_level = getattr(logging, settings.server_log_level.upper(), logging.INFO)
    
    # 로그 설정 (Pydantic Settings 사용)
    log_to_file = settings.log_to_file
    log_dir = settings.log_dir
    log_file = settings.log_file
    log_path = os.path.join(log_dir, log_file)
    
    # 로그 디렉토리 생성 (파일 로깅이 활성화된 경우만)
    if log_to_file:
        os.makedirs(log_dir, exist_ok=True)
    
    # 핸들러 설정
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": app_log_level,
            "formatter": "colored",
            "stream": "ext://sys.stdout"
        }
    }
    
    # 파일 로깅이 활성화된 경우 파일 핸들러 추가
    # ==========================================
    # 파일 로깅은 다음 경우에만 사용:
    # 1. 온프레미스 환경 (Kubernetes 로그 수집 시스템 없음)
    # 2. 특별한 로그 분석 요구사항
    # 3. 개발 환경 (디버깅 편의)
    if log_to_file:
        # 로그 로테이션 설정 가져오기
        log_rotation = settings.log_rotation
        log_retention_days = settings.log_retention_days
        
        if log_rotation == "size":
            # ==========================================
            # 크기 기반 로테이션 (RotatingFileHandler)
            # - 파일 크기가 10MB에 도달하면 새 파일 생성
            # - 최대 5개 파일 보관 (총 50MB)
            # - 사용 사례: 로그량이 많고 크기 제한이 중요한 경우
            # ==========================================
            handlers["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": app_log_level,
                "formatter": "default",
                "filename": log_path,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5       # 최대 5개 파일 보관
            }
        else:
            # ==========================================
            # 시간 기반 로테이션 (TimedRotatingFileHandler)
            # - 날짜별/주별/월별로 로그 파일 분리
            # - 설정된 기간만큼 로그 파일 보관
            # - 사용 사례: 로그 분석, 감사, 장기 보관이 필요한 경우
            # ==========================================
            when_map = {
                "daily": "midnight",   # 매일 자정 (00:00)
                "weekly": "W0",        # 매주 월요일 (W0 = 월요일)
                "monthly": "M1"        # 매월 1일 (M1 = 매월 1일)
            }
            when = when_map.get(log_rotation, "midnight")
            
            handlers["file"] = {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": app_log_level,
                "formatter": "default",
                "filename": log_path,
                "when": when,                    # 로테이션 시점
                "interval": 1,                   # 간격 (1일/1주/1월)
                "backupCount": log_retention_days,  # 보관 기간
                "encoding": "utf-8"              # UTF-8 인코딩
            }
    
    # 동적 로깅 설정
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s",
            },
            "colored": {
                "()": "coloredlogs.ColoredFormatter",
                "format": "%(asctime)s.%(msecs)03d %(levelname)-5s %(process)5d --- [%(funcName)20s] %(name)-40s : %(message)s"
            }
        },
        "handlers": handlers,
        "loggers": {
            "": {  # root logger (앱 로그)
                "level": app_log_level,
                "handlers": ["console"] + (["file"] if log_to_file else [])
            },
            "uvicorn": {  # uvicorn 서버 로그
                "level": server_log_level,
                "handlers": ["console"] + (["file"] if log_to_file else []),
                "propagate": False
            },
            "uvicorn.access": {  # uvicorn access 로그
                "level": server_log_level,
                "handlers": ["console"] + (["file"] if log_to_file else []),
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    
    # 로깅 설정 완료 로그
    logger = logging.getLogger(__name__)
    logger.info("로깅 설정 완료 - 앱 로그 레벨: {}, 서버 로그 레벨: {}".format(settings.app_log_level.upper(), settings.server_log_level.upper()))

# 동적 로깅 설정 적용
setup_logging()
logger = logging.getLogger(__name__)

# ==========================================
# 애플리케이션 시작 시 오래된 로그 파일 정리
# ==========================================
# 목적: 디스크 공간 절약 및 로그 파일 관리
# 실행 시점: 애플리케이션 시작 시 (서버 재시작할 때마다)
# 동작: LOG_RETENTION_DAYS 설정에 따라 오래된 로그 파일 자동 삭제
# 안전성: 현재 로그 파일은 절대 삭제하지 않음
cleanup_old_logs()

# Pydantic Settings가 자동으로 .env 파일과 환경 변수를 로드합니다
# 간단한 예외 처리는 FastAPI 기본값 사용


def create_app():
    logger.info("Creating FastAPI application...")
    
    # 디버그 모드 설정
    debug_mode = settings.app_debug
    logger.info("애플리케이션 디버그 모드: {}".format('활성화' if debug_mode else '비활성화'))
    
    app = FastAPI(
        title="LLM Chat API",
        description="AI-powered chat service with streaming support",
        version="1.0.0",
        debug=debug_mode,  # FastAPI 디버그 모드 활성화
        root_path=settings.app_root_path  # 리버스 프록시 환경에서 사용
    )
    
    logger.info("FastAPI application created successfully")
    
    # Global exception handlers 등록
    app = set_global_exception_handlers(app)
    logger.info("Global exception handlers registered successfully")
  
    # API 버전 경로 설정
    # APP_ROOT_PATH로 관리하므로 라우터에서는 /v1만 사용
    api_prefix = "/v1"
    
    # LLM Chat 라우터 추가 (채팅 전용)
    from ai_backend.api.routers.chat_router import router as chat_router
    app.include_router(chat_router, prefix=api_prefix)
    
    # Cache 라우터 추가 (채팅 전용)
    from ai_backend.api.routers.cache_router import router as cache_router
    app.include_router(cache_router, prefix=api_prefix)
    
    # Document 라우터 추가 (문서 관리)
    from ai_backend.api.routers.document_router import router as document_router
    app.include_router(document_router, prefix=api_prefix)
    
    # User 라우터 추가 (사용자 관리)
    from ai_backend.api.routers.user_router import router as user_router
    app.include_router(user_router, prefix=api_prefix)
    
    # Group 라우터 추가 (그룹 관리)
    from ai_backend.api.routers.group_router import router as group_router
    app.include_router(group_router, prefix=api_prefix)
    
    # CORS 설정 - 설정 파일에서 가져오기
    origins = settings.get_cors_origins()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # HTML 클라이언트 서빙
    @app.get("/")
    async def read_root():
        return FileResponse("llm_chat_client.html")
    
    @app.get("/chat")
    async def read_chat():
        return FileResponse("llm_chat_client.html")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "ai-backend"}
    
    # 디버그 모드에서만 추가 엔드포인트 제공
    if debug_mode:
        @app.get("/debug/info")
        async def debug_info():
            """디버그 모드에서만 사용 가능한 시스템 정보"""
            import platform
            import sys
            return {
                "debug_mode": True,
                "python_version": sys.version,
                "platform": platform.platform(),
                "app_version": settings.app_version,
                "log_level": settings.app_log_level,
                "server_log_level": settings.server_log_level,
                "cache_enabled": settings.cache_enabled,
                "database_host": settings.database_host,
                "redis_host": settings.redis_host
            }
        
        @app.get("/debug/logs")
        async def debug_logs():
            """디버그 모드에서만 사용 가능한 로그 레벨 테스트"""
            logger.debug("DEBUG 로그 테스트")
            logger.info("INFO 로그 테스트")
            logger.warning("WARNING 로그 테스트")
            logger.error("ERROR 로그 테스트")
            return {"message": "로그 테스트 완료 - 콘솔을 확인하세요"}
        
        @app.post("/debug/cleanup-logs")
        async def debug_cleanup_logs():
            """
            디버그 모드에서만 사용 가능한 로그 정리 엔드포인트
            
            ==========================================
            기능:
            - 수동으로 오래된 로그 파일 정리 실행
            - 개발/테스트 환경에서 로그 정리 기능 테스트 가능
            - 운영 중 디스크 공간 부족 시 긴급 정리 가능
            
            사용법:
            curl -X POST http://localhost:8000/debug/cleanup-logs
            
            주의사항:
            - 디버그 모드(APP_DEBUG=true)에서만 접근 가능
            - 파일 로깅(LOG_TO_FILE=true)이 활성화된 경우에만 동작
            - 현재 로그 파일은 절대 삭제하지 않음
            
            응답:
            - 성공: {"message": "로그 정리 완료 - 콘솔을 확인하세요"}
            - 상세한 정리 결과는 애플리케이션 로그에서 확인 가능
            """
            logger.info("수동 로그 정리 요청됨 (디버그 엔드포인트)")
            cleanup_old_logs()
            return {"message": "로그 정리 완료 - 콘솔을 확인하세요"}
    
    return app

app = create_app()
    
