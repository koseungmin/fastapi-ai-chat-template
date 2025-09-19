# _*_ coding: utf-8 _*_
"""로깅 유틸리티 함수들."""
import logging
from ai_backend.config.simple_settings import settings

logger = logging.getLogger(__name__)


def log_error(message: str, exception: Exception = None):
    """
    에러 로그를 기록하는 유틸리티 함수
    
    Args:
        message: 로그 메시지
        exception: 예외 객체 (선택사항)
    """
    if exception:
        logger.error(f"{message}: {exception}", exc_info=settings.log_include_exc_info)
    else:
        logger.error(message)


def log_warning(message: str, exception: Exception = None):
    """
    경고 로그를 기록하는 유틸리티 함수
    
    Args:
        message: 로그 메시지
        exception: 예외 객체 (선택사항)
    """
    if exception:
        logger.warning(f"{message}: {exception}", exc_info=settings.log_include_exc_info)
    else:
        logger.warning(message)


def log_info(message: str, exception: Exception = None):
    """
    정보 로그를 기록하는 유틸리티 함수
    
    Args:
        message: 로그 메시지
        exception: 예외 객체 (선택사항)
    """
    if exception:
        logger.info(f"{message}: {exception}", exc_info=settings.log_include_exc_info)
    else:
        logger.info(message)


def log_debug(message: str, exception: Exception = None):
    """
    디버그 로그를 기록하는 유틸리티 함수
    
    Args:
        message: 로그 메시지
        exception: 예외 객체 (선택사항)
    """
    if exception:
        logger.debug(f"{message}: {exception}", exc_info=settings.log_include_exc_info)
    else:
        logger.debug(message)
