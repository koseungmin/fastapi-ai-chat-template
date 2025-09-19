# _*_ coding: utf-8 _*_
"""Redis client for caching and session management."""
import redis
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


class RedisClient:
    """Redis 클라이언트 - 캐싱 및 세션 관리"""
    
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.password = os.getenv("REDIS_PASSWORD", None)
        
        # 환경변수에서 최대 연결 수 가져오기 (기본값: 500)
        max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "500"))
        socket_timeout = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
        socket_connect_timeout = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))
        
        self.redis_client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True,
            socket_connect_timeout=socket_connect_timeout,
            socket_timeout=socket_timeout,
            retry_on_timeout=True,
            max_connections=max_connections  # 100 → 500 (1000명 대응)
        )
    
    def ping(self) -> bool:
        """Redis 연결 상태 확인"""
        try:
            return self.redis_client.ping()
        except Exception:
            return False
    
    def set_session(self, chat_id: str, data: Dict[str, Any], expire_seconds: int = 3600) -> bool:
        """세션 데이터 저장"""
        try:
            key = f"session:{chat_id}"
            self.redis_client.setex(key, expire_seconds, json.dumps(data))
            return True
        except Exception:
            return False
    
    def get_session(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """세션 데이터 조회"""
        try:
            key = f"session:{chat_id}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
    
    def delete_session(self, chat_id: str) -> bool:
        """세션 데이터 삭제"""
        try:
            key = f"session:{chat_id}"
            return bool(self.redis_client.delete(key))
        except Exception:
            return False
    
    def set_chat_cache(self, chat_id: str, messages: List[Dict[str, Any]], expire_seconds: int = 1800) -> bool:
        """채팅 메시지 캐시 저장"""
        try:
            key = f"chat:{chat_id}"
            self.redis_client.setex(key, expire_seconds, json.dumps(messages))
            return True
        except Exception:
            return False
    
    def get_chat_cache(self, chat_id: str) -> Optional[List[Dict[str, Any]]]:
        """채팅 메시지 캐시 조회"""
        try:
            key = f"chat:{chat_id}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
    
    def delete_chat_cache(self, chat_id: str) -> bool:
        """채팅 메시지 캐시 삭제"""
        try:
            key = f"chat:{chat_id}"
            return bool(self.redis_client.delete(key))
        except Exception:
            return False
    
    def set_user_chats_cache(self, user_id: str, chats: List[Dict[str, Any]], expire_seconds: int = 600) -> bool:
        """사용자 채팅 목록 캐시 저장"""
        try:
            key = f"user_chats:{user_id}"
            self.redis_client.setex(key, expire_seconds, json.dumps(chats))
            return True
        except Exception:
            return False
    
    def get_user_chats_cache(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """사용자 채팅 목록 캐시 조회"""
        try:
            key = f"user_chats:{user_id}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
    
    def delete_user_chats_cache(self, user_id: str) -> bool:
        """사용자 채팅 목록 캐시 삭제"""
        try:
            key = f"user_chats:{user_id}"
            return bool(self.redis_client.delete(key))
        except Exception:
            return False
    
    def get_chat_messages(self, chat_id: str) -> Optional[List[Dict[str, Any]]]:
        """채팅 메시지 조회 (get_chat_cache와 동일)"""
        return self.get_chat_cache(chat_id)
    
    def set_chat_messages(self, chat_id: str, messages: List[Dict[str, Any]], expire_seconds: int = 1800) -> bool:
        """채팅 메시지 저장 (set_chat_cache와 동일)"""
        return self.set_chat_cache(chat_id, messages, expire_seconds)
    
    def delete_chat_messages(self, chat_id: str) -> bool:
        """채팅 메시지 삭제 (delete_chat_cache와 동일)"""
        return self.delete_chat_cache(chat_id)
    
    def increment_counter(self, key: str, expire_seconds: int = 3600) -> int:
        """카운터 증가"""
        try:
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, expire_seconds)
            result = pipe.execute()
            return result[0]
        except Exception:
            return 0
    
    def get_counter(self, key: str) -> int:
        """카운터 값 조회"""
        try:
            value = self.redis_client.get(key)
            return int(value) if value else 0
        except Exception:
            return 0
    
    def close(self):
        """Redis 연결 종료"""
        try:
            self.redis_client.close()
        except Exception:
            pass


# 전역 Redis 클라이언트 인스턴스
redis_client = None


def get_redis_client() -> RedisClient:
    """Redis 클라이언트 의존성 주입"""
    global redis_client
    if redis_client is None:
        redis_client = RedisClient()
    return redis_client
