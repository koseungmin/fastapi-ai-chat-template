# _*_ coding: utf-8 _*_
"""Cache control API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from ai_backend.core.dependencies import get_database, get_redis_client
from ai_backend.config import settings
from ai_backend.database.base import Database
from ai_backend.cache.redis_client import RedisClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["cache-control"])


def get_cache_config():
    """캐시 설정 의존성 주입"""
    return settings


@router.get("/cache/status")
def get_cache_status(
    redis_client: RedisClient = Depends(get_redis_client),
    cache_config = Depends(get_cache_config)
):
    """캐시 상태 조회"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    if not redis_client or not redis_client.ping():
        return {
            "status": "success",
            "data": {"enabled": False, "message": "Redis not available"}
        }
    
    # Redis 정보 조회
    info = redis_client.redis_client.info()
    keys = redis_client.redis_client.keys("*")
    
    return {
        "status": "success",
        "data": {
            "enabled": True,
            "redis_version": info.get("redis_version"),
            "used_memory": info.get("used_memory_human"),
            "total_keys": len(keys),
            "cache_config": {
                "enabled": cache_config.cache_enabled,
                "ttl_chat_messages": cache_config.cache_ttl_chat_messages,
                "ttl_user_chats": cache_config.cache_ttl_user_chats,
                "redis_host": cache_config.redis_host,
                "redis_port": cache_config.redis_port,
                "redis_db": cache_config.redis_db
            }
        }
    }


@router.post("/cache/clear")
def clear_cache(
    redis_client: RedisClient = Depends(get_redis_client)
):
    """모든 캐시 삭제"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    if not redis_client or not redis_client.ping():
        return {
            "status": "warning",
            "message": "Redis가 사용할 수 없습니다."
        }
    
    # 모든 캐시 키 삭제
    keys = redis_client.redis_client.keys("*")
    if keys:
        redis_client.redis_client.delete(*keys)
        return {
            "status": "success",
            "message": f"{len(keys)}개의 캐시가 삭제되었습니다."
        }
    else:
        return {
            "status": "info",
            "message": "삭제할 캐시가 없습니다."
        }


@router.get("/cache/test")
def test_cache(
    redis_client: RedisClient = Depends(get_redis_client)
):
    """캐시 테스트"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    if not redis_client or not redis_client.ping():
        return {
            "status": "info",
            "message": "Redis가 사용할 수 없습니다.",
            "cache_enabled": False
        }

    # 테스트용 데이터
    test_key = "test:cache:123"
    test_data = {"message": "안녕하세요!", "timestamp": "2024-01-01T00:00:00"}

    # Redis에 테스트 데이터 저장
    redis_client.redis_client.setex(test_key, 60, str(test_data))

    # 저장된 데이터 조회
    cached_data = redis_client.redis_client.get(test_key)

    # 테스트 데이터 삭제
    redis_client.redis_client.delete(test_key)

    return {
        "status": "success",
        "message": "캐시 테스트가 성공적으로 완료되었습니다.",
        "cache_enabled": True,
        "test_data": cached_data
    }


@router.get("/cache/config")
def get_cache_config(
    cache_config=Depends(get_cache_config)
):
    """캐시 설정 조회"""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    return {
        "status": "success",
        "data": {
            "enabled": cache_config.cache_enabled,
            "ttl_chat_messages": cache_config.cache_ttl_chat_messages,
            "ttl_user_chats": cache_config.cache_ttl_user_chats,
            "redis_host": cache_config.redis_host,
            "redis_port": cache_config.redis_port,
            "redis_db": cache_config.redis_db
        }
    }


@router.get("/cache/keys")
def get_cache_keys(
    pattern: str = "*",
    redis_client: RedisClient = Depends(get_redis_client)
):
    """캐시 키 목록 조회"""
    if not redis_client or not redis_client.ping():
        return {
            "status": "error",
            "message": "Redis가 사용할 수 없습니다."
        }

    try:
        # 패턴에 맞는 키들 조회
        keys = redis_client.redis_client.keys(pattern)

        # 키별 정보 수집
        key_info = []
        for key in keys:
            # 키를 문자열로 변환 (bytes인 경우만 decode)
            key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
            ttl = redis_client.redis_client.ttl(key)

            # 타입 정보를 문자열로 변환
            key_type_raw = redis_client.redis_client.type(key)
            key_type = key_type_raw.decode('utf-8') if isinstance(key_type_raw, bytes) else str(key_type_raw)

            key_info.append({
                "key": key_str,
                "type": key_type,
                "ttl": ttl if ttl > 0 else "persistent"
            })

        return {
            "status": "success",
            "data": {
                "pattern": pattern,
                "total_keys": len(keys),
                "keys": key_info
            }
        }
    except Exception as e:
        # Global Exception Handler가 처리하도록 예외를 다시 발생
        from ai_backend.types.response.exceptions import HandledException
        from ai_backend.types.response.response_code import ResponseCode
        raise HandledException(ResponseCode.CACHE_QUERY_ERROR, e=e)


@router.get("/cache/data/{key}")
def get_cache_data(
    key: str,
    redis_client: RedisClient = Depends(get_redis_client)
):
    """특정 캐시 데이터 조회"""
    if not redis_client or not redis_client.ping():
        return {
            "status": "error",
            "message": "Redis가 사용할 수 없습니다."
        }
    
    try:
        # 키 존재 확인
        if not redis_client.redis_client.exists(key):
            return {
                "status": "error",
                "message": f"키 '{key}'가 존재하지 않습니다."
            }
        
        # 키 타입 확인
        key_type_raw = redis_client.redis_client.type(key)
        key_type = key_type_raw.decode('utf-8') if isinstance(key_type_raw, bytes) else str(key_type_raw)
        
        # 타입별 데이터 조회
        if key_type == "string":
            data = redis_client.redis_client.get(key)
            if isinstance(data, bytes):
                data = data.decode('utf-8')
        elif key_type == "list":
            data = redis_client.redis_client.lrange(key, 0, -1)
            data = [item.decode('utf-8') if isinstance(item, bytes) else item for item in data]
        elif key_type == "hash":
            data = redis_client.redis_client.hgetall(key)
            data = {k.decode('utf-8') if isinstance(k, bytes) else k: 
                   v.decode('utf-8') if isinstance(v, bytes) else v 
                   for k, v in data.items()}
        elif key_type == "set":
            data = redis_client.redis_client.smembers(key)
            data = [item.decode('utf-8') if isinstance(item, bytes) else item for item in data]
        else:
            data = "지원하지 않는 데이터 타입입니다."
        
        # TTL 정보
        ttl = redis_client.redis_client.ttl(key)
        
        return {
            "status": "success",
            "data": {
                "key": key,
                "type": key_type,
                "ttl": ttl if ttl > 0 else "persistent",
                "value": data
            }
        }
    except Exception as e:
        # Global Exception Handler가 처리하도록 예외를 다시 발생
        from ai_backend.types.response.exceptions import HandledException
        from ai_backend.types.response.response_code import ResponseCode
        raise HandledException(ResponseCode.CACHE_QUERY_ERROR, e=e)


@router.get("/cache/chat/{chat_id}")
def get_chat_cache(
    chat_id: str,
    redis_client: RedisClient = Depends(get_redis_client)
):
    """특정 채팅방 캐시 데이터 조회"""
    if not redis_client or not redis_client.ping():
        return {
            "status": "error",
            "message": "Redis가 사용할 수 없습니다."
        }
    
    try:
        # 채팅방 관련 키들 조회
        chat_keys = [
            f"chat_messages:{chat_id}",
            f"generation:{chat_id}",
            f"cancel:{chat_id}"
        ]
        
        chat_data = {}
        for key in chat_keys:
            if redis_client.redis_client.exists(key):
                key_type_raw = redis_client.redis_client.type(key)
                key_type = key_type_raw.decode('utf-8') if isinstance(key_type_raw, bytes) else str(key_type_raw)
                ttl = redis_client.redis_client.ttl(key)
                
                if key_type == "string":
                    data = redis_client.redis_client.get(key)
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                else:
                    data = "복잡한 데이터 타입"
                
                chat_data[key] = {
                    "type": key_type,
                    "ttl": ttl if ttl > 0 else "persistent",
                    "value": data
                }
        
        return {
            "status": "success",
            "data": {
                "chat_id": chat_id,
                "keys": chat_data,
                "total_keys": len(chat_data)
            }
        }
    except Exception as e:
        # Global Exception Handler가 처리하도록 예외를 다시 발생
        from ai_backend.types.response.exceptions import HandledException
        from ai_backend.types.response.response_code import ResponseCode
        raise HandledException(ResponseCode.CACHE_QUERY_ERROR, e=e)


@router.delete("/cache/data/{key}")
def delete_cache_data(
    key: str,
    redis_client: RedisClient = Depends(get_redis_client)
):
    """특정 캐시 데이터 삭제"""
    if not redis_client or not redis_client.ping():
        return {
            "status": "error",
            "message": "Redis가 사용할 수 없습니다."
        }
    
    try:
        # 키 존재 확인
        if not redis_client.redis_client.exists(key):
            return {
                "status": "error",
                "message": f"키 '{key}'가 존재하지 않습니다."
            }
        
        # 키 삭제
        deleted = redis_client.redis_client.delete(key)
        
        if deleted:
            return {
                "status": "success",
                "message": f"키 '{key}'가 삭제되었습니다."
            }
        else:
            return {
                "status": "error",
                "message": f"키 '{key}' 삭제에 실패했습니다."
            }
    except Exception as e:
        # Global Exception Handler가 처리하도록 예외를 다시 발생
        from ai_backend.types.response.exceptions import HandledException
        from ai_backend.types.response.response_code import ResponseCode
        raise HandledException(ResponseCode.CACHE_QUERY_ERROR, e=e)


