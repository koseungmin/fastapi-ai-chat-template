# Exception 처리 가이드

이 문서는 FastAPI 템플릿의 Exception 처리 시스템 사용법을 설명합니다.  
**신규 개발자는 이 가이드를 따라 일관성 있는 예외 처리를 구현하세요.**

## 📋 목차

1. [빠른 시작](#빠른-시작)
2. [Exception 구조 개요](#exception-구조-개요)
3. [계층별 Exception 처리 전략](#계층별-exception-처리-전략)
4. [ResponseCode 사용법](#responsecode-사용법)
5. [HandledException 사용법](#handledexception-사용법)
6. [실제 사용 예시](#실제-사용-예시)
7. [HTTP 상태 코드 매핑](#http-상태-코드-매핑)
8. [모범 사례](#모범-사례)
9. [문제 해결](#문제-해결)

## 빠른 시작

### 🚀 5분 만에 시작하기

#### 1. 기본 예외 발생
```python
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode

# 비즈니스 규칙 위반 시
if user_exists:
    raise HandledException(ResponseCode.USER_ALREADY_EXISTS, msg="사용자가 이미 존재합니다")

# 데이터베이스 오류 시 (Repository Layer)
except SQLAlchemyError as e:
    raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
```

#### 2. 자동 로깅 시스템
```python
# ❌ 이전 방식 (수동 로깅)
try:
    # 비즈니스 로직
except Exception as e:
    logger.error(f"Database error: {e}", exc_info=True)
    raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

# ✅ 현재 방식 (자동 로깅)
try:
    # 비즈니스 로직
except Exception as e:
    # 로깅은 Global Exception Handler에서 자동 처리
    raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
```

#### 2. 계층별 예외 처리 패턴
```python
# Repository Layer (user_crud.py)
def create_user(self, user_id: str, employee_id: str, name: str) -> User:
    try:
        # 데이터베이스 작업
        user = User(
            user_id=user_id,
            employee_id=employee_id,
            name=name,
            create_dt=datetime.now(),
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    except Exception as e:
        # 로깅은 Global Exception Handler에서 자동 처리
        self.db.rollback()
        raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

# Service Layer (user_service.py)
def create_user(self, user_id: str, employee_id: str, name: str):
    try:
        # 비즈니스 로직
        # 사번 중복 체크
        if self.user_crud.check_employee_id_exists(employee_id):
            raise HandledException(
                ResponseCode.USER_ALREADY_EXISTS, 
                msg=f"사번 {employee_id}는 이미 사용 중입니다."
            )
        
        # 사용자 ID 중복 체크
        if self.user_crud.get_user(user_id):
            raise HandledException(
                ResponseCode.USER_ALREADY_EXISTS, 
                msg=f"사용자 ID {user_id}는 이미 사용 중입니다."
            )
        
        user = self.user_crud.create_user(user_id, employee_id, name)
        return user
    except HandledException:
        raise  # 그대로 전파
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)

# Router Layer (user_router.py)
@router.post("/users", response_model=UserCreateResponse)
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(get_user_service)
):
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    user = user_service.create_user(
        user_id=request.user_id,
        employee_id=request.employee_id,
        name=request.name
    )
    
    return UserCreateResponse(
        user_id=user.user_id,
        employee_id=user.employee_id,
        name=user.name
    )
```

#### 3. 자동 응답 변환
```json
// 예외 발생 시 자동으로 생성되는 응답
{
    "timestamp": 1640995200000,
    "code": -1202,
    "message": "이미 존재하는 사용자입니다.: 사용자가 이미 존재합니다",
    "traceId": null,
    "data": null
}
```

### ⚡ 핵심 원칙 (기억하세요!)

1. **Repository Layer**: SQLAlchemy 예외 → `DATABASE_*` 코드
2. **Service Layer**: 비즈니스 규칙 위반 → `USER_*`, `CHAT_*` 코드
3. **Router Layer**: 예외 처리 없이 전파만
4. **Global Handler**: 자동으로 `ErrorResponse` 변환

## Exception 구조 개요

### 핵심 컴포넌트

- **`ResponseCode`**: 에러 코드와 메시지를 정의하는 Enum
- **`HandledException`**: 애플리케이션에서 관리하는 예외 클래스
- **`UnHandledException`**: 예상치 못한 예외를 처리하는 래퍼 클래스
- **`ErrorResponse`**: 표준화된 에러 응답 생성
- **Global Exception Handlers**: FastAPI에서 예외를 자동으로 처리

### 파일 구조

```
ai_backend/
├── types/response/
│   ├── response_code.py      # 에러 코드 정의
│   ├── exceptions.py         # Exception 클래스들
│   └── base.py              # Response 클래스들
├── core/
│   └── global_exception_handlers.py  # Global exception handlers
├── database/crud/            # Repository Layer
├── api/services/             # Service Layer
└── api/routers/              # Router Layer
```

## 자동 로깅 시스템

### 🔄 Global Exception Handler

모든 예외는 Global Exception Handler에서 자동으로 로깅됩니다.

#### 환경변수로 로깅 제어
```bash
# 개발 환경 (상세 로그)
LOG_INCLUDE_EXC_INFO=true

# 운영 환경 (간단 로그)
LOG_INCLUDE_EXC_INFO=false
```

#### 로깅 구조
```python
# 서버 콘솔 (개발자용)
2025-09-18 10:30:15.123 ERROR [exceptions] HandledException [-1001]: 사용자 생성에 실패했습니다.
Request: ==================================================
Request {method: POST} {url: http://localhost:8000/api/v1/users}
[상세한 스택 트레이스...]  # LOG_INCLUDE_EXC_INFO=true일 때만

# 클라이언트 응답 (사용자용)
{
  "status": "error",
  "code": -1001,
  "message": "사용자 생성에 실패했습니다.",
  "data": null
}
```

## 계층별 Exception 처리 전략

### 🏗️ 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                    Router Layer (Controller)                │
│  - HTTP 요청/응답 처리                                          
│  - Service 예외를 그대로 전파                                    │
│  - Global Handler가 자동 처리                                  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer (Business Logic)            │
│  - 비즈니스 로직 예외 처리                                    │
│  - Repository 예외를 그대로 전파 (이미 변환됨)                │
│  - 비즈니스 규칙 검증 및 예외 발생                            │
│  - 예상치 못한 예외는 UNDEFINED_ERROR로 처리                  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                  Repository Layer (Data Access)             │
│  - 데이터베이스 관련 예외 처리                                │
│  - SQLAlchemy 예외를 HandledException으로 변환               │
│  - 트랜잭션 롤백 처리                                        │
│  - DATABASE_* 예외 코드 사용                                 │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Global Exception Handler                 │
│  - HandledException을 ErrorResponse로 변환                  │
│  - HTTP 상태 코드 자동 설정                                  │
│  - 로깅 및 모니터링                                          │
└─────────────────────────────────────────────────────────────┘
```

### 📊 계층별 책임 분담

| 계층 | 책임 | 처리하는 예외 | 전파 방식 |
|------|------|---------------|-----------|
| **Repository** | 데이터베이스 예외 처리 | `DATABASE_*` 관련 | HandledException으로 변환 |
| **Service** | 비즈니스 로직 예외 처리 | `USER_*`, `CHAT_*`, `VALIDATION_*` 등 | Repository 예외를 그대로 전파, 예상치 못한 예외는 `UNDEFINED_ERROR`로 변환 |
| **Router** | HTTP 요청/응답 처리 | 없음 | Service 예외를 그대로 전파 |
| **Global Handler** | 최종 예외 처리 | 모든 예외 타입 | ErrorResponse 생성 및 HTTP 응답 |

### 🔧 Global Exception Handler 처리 예외 타입

#### 1. **애플리케이션 예외**
- `HandledException` - 애플리케이션에서 의도적으로 발생시킨 예외
- `UnHandledException` - 예상치 못한 예외를 래핑한 예외

#### 2. **HTTP 예외**
- `HTTPException` - FastAPI HTTP 예외
- `StarletteHTTPException` - Starlette HTTP 예외
- `HTTPRequestValidationError` - 요청 검증 예외 (422)

#### 3. **Python 내장 예외**
- `ValueError` - 값 에러
- `KeyError` - 키 에러
- `ConnectionError` - 연결 에러
- `FileNotFoundError` - 파일 없음 에러

#### 4. **Redis 예외** (추가됨)
- `redis.exceptions.ResponseError` - Redis 명령어 에러
- `redis.exceptions.ConnectionError` - Redis 연결 에러
- `redis.exceptions.TimeoutError` - Redis 타임아웃 에러

#### 5. **기타 모든 예외**
- `Exception` - 모든 다른 예외를 포괄하는 범용 핸들러

### 🔄 예외 처리 흐름

1. **Repository Layer**: SQLAlchemy 예외 → HandledException 변환
2. **Service Layer**: 비즈니스 로직 예외 + Repository 예외 처리
3. **Router Layer**: Service 예외를 그대로 전파
4. **Global Handler**: HandledException → ErrorResponse 변환

자세한 내용은 이 가이드의 [계층별 Exception 처리 전략](#계층별-exception-처리-전략) 섹션을 참조하세요.

## ResponseCode 사용법

### 기본 사용법

```python
from ai_backend.types.response.response_code import ResponseCode

# 성공
ResponseCode.SUCCESS  # (1, "성공")

# 실패
ResponseCode.FAIL     # (-1, "실패")

# 정의되지 않은 오류
ResponseCode.UNDEFINED_ERROR  # (-2, "정의되지 않은 오류입니다.")
```

### 비즈니스 로직별 에러 코드

#### 사용자 관련 에러 (-1200 ~ -1299)
```python
ResponseCode.USER_NOT_FOUND           # (-1201, "사용자를 찾을 수 없습니다.")
ResponseCode.USER_ALREADY_EXISTS      # (-1202, "이미 존재하는 사용자입니다.")
ResponseCode.USER_INVALID_CREDENTIALS # (-1203, "잘못된 인증 정보입니다.")
```

#### 채팅 관련 에러 (-1300 ~ -1399)
```python
ResponseCode.CHAT_SESSION_NOT_FOUND    # (-1301, "채팅 세션을 찾을 수 없습니다.")
ResponseCode.CHAT_MESSAGE_INVALID      # (-1302, "잘못된 채팅 메시지입니다.")
ResponseCode.CHAT_RATE_LIMIT_EXCEEDED  # (-1303, "채팅 요청 한도를 초과했습니다.")
```

#### 데이터베이스 관련 에러 (-1400 ~ -1499)
```python
ResponseCode.DATABASE_CONNECTION_ERROR  # (-1401, "데이터베이스 연결 오류가 발생했습니다.")
ResponseCode.DATABASE_QUERY_ERROR       # (-1402, "데이터베이스 쿼리 오류가 발생했습니다.")
ResponseCode.DATABASE_TRANSACTION_ERROR # (-1403, "데이터베이스 트랜잭션 오류가 발생했습니다.")
```

#### 캐시 관련 에러 (-1500 ~ -1599)
```python
ResponseCode.CACHE_CONNECTION_ERROR  # (-1501, "캐시 연결 오류가 발생했습니다.")
ResponseCode.CACHE_OPERATION_ERROR   # (-1502, "캐시 작업 오류가 발생했습니다.")
```

#### 검증 관련 에러 (-1600 ~ -1699)
```python
ResponseCode.VALIDATION_ERROR        # (-1601, "입력 데이터 검증 오류가 발생했습니다.")
ResponseCode.REQUIRED_FIELD_MISSING  # (-1602, "필수 필드가 누락되었습니다.")
ResponseCode.INVALID_DATA_FORMAT     # (-1603, "잘못된 데이터 형식입니다.")
```

#### 외부 서비스 관련 에러 (-1700 ~ -1799)
```python
ResponseCode.EXTERNAL_SERVICE_ERROR        # (-1701, "외부 서비스 오류가 발생했습니다.")
ResponseCode.EXTERNAL_SERVICE_TIMEOUT      # (-1702, "외부 서비스 응답 시간 초과가 발생했습니다.")
ResponseCode.EXTERNAL_SERVICE_UNAVAILABLE  # (-1703, "외부 서비스를 사용할 수 없습니다.")
```

## HandledException 사용법

### 기본 사용법

```python
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode

# 기본 사용
raise HandledException(ResponseCode.USER_NOT_FOUND)

# 추가 메시지와 함께
raise HandledException(ResponseCode.USER_NOT_FOUND, msg="사용자 ID: 123")

# 원본 예외와 함께
try:
    # 어떤 작업
    pass
except Exception as e:
    raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

# 커스텀 HTTP 상태 코드와 함께
raise HandledException(
    ResponseCode.USER_NOT_FOUND, 
    http_status_code=404
)
```

### 파라미터 설명

- **`resp_code`**: `ResponseCode` - 에러 코드와 메시지
- **`e`**: `Exception` (선택사항) - 원본 예외 객체
- **`code`**: `int` (선택사항) - 커스텀 에러 코드
- **`msg`**: `str` (선택사항) - 추가 메시지
- **`http_status_code`**: `int` (선택사항) - HTTP 상태 코드 (기본값: 400)

## 실제 사용 예시

### 1. 사용자 생성 API (Router → Service → Repository)

```python
# Router Layer (user_router.py)
@router.post("/users", response_model=UserCreateResponse)
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(get_user_service)
):
    """새로운 사용자를 생성합니다."""
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    user = user_service.create_user(
        user_id=request.user_id,
        employee_id=request.employee_id,
        name=request.name
    )
    
    return UserCreateResponse(
        user_id=user.user_id,
        employee_id=user.employee_id,
        name=user.name
    )

# Service Layer (user_service.py)
def create_user(self, user_id: str, employee_id: str, name: str):
    """사용자 생성"""
    try:
        with self.db.session() as session:
            user_crud = UserCRUD(session)
            
            # 사번 중복 체크 (비즈니스 규칙)
            if user_crud.check_employee_id_exists(employee_id):
                raise HandledException(
                    ResponseCode.USER_ALREADY_EXISTS, 
                    msg=f"사번 {employee_id}는 이미 사용 중입니다."
                )
            
            # 사용자 ID 중복 체크 (비즈니스 규칙)
            if user_crud.get_user(user_id):
                raise HandledException(
                    ResponseCode.USER_ALREADY_EXISTS, 
                    msg=f"사용자 ID {user_id}는 이미 사용 중입니다."
                )
            
            # 사용자 생성
            user = user_crud.create_user(user_id, employee_id, name)
            return user
            
    except HandledException:
        raise  # HandledException은 그대로 전파
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        # Service Layer에서는 구체적인 예외 타입을 모르므로 일반적인 오류로 처리
        # Repository Layer에서 이미 구체적인 예외를 HandledException으로 변환했으므로
        # 여기서는 예상치 못한 예외만 처리
        raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)

# Repository Layer (user_crud.py)
def create_user(self, user_id: str, employee_id: str, name: str) -> User:
    """사용자 생성"""
    try:
        user = User(
            user_id=user_id,
            employee_id=employee_id,
            name=name,
            create_dt=datetime.now(),
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    except IntegrityError as e:
        logger.error(f"Database integrity error creating user: {str(e)}")
        self.db.rollback()
        raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    except SQLAlchemyError as e:
        logger.error(f"Database error creating user: {str(e)}")
        self.db.rollback()
        raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        self.db.rollback()
        raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
```

### 2. 채팅 메시지 전송 API (Router → Service)

```python
# Router Layer (chat_router.py)
@router.post("/chat/{chat_id}/message", response_model=AIResponse)
async def send_message(
    chat_id: str,
    request: UserMessageRequest,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)
):
    """사용자 메시지를 전송하고 AI 응답을 받습니다."""
    logger.info(f"Received message for chat {chat_id}: {request.message[:50]}...")
    
    # Service Layer에서 전파된 HandledException을 그대로 전파
    # Global Exception Handler가 자동으로 처리
    ai_response = await llm_chat_service.send_message_simple(
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

# Service Layer (llm_chat_service.py) - 예시
async def send_message_simple(self, chat_id: str, message: str, user_id: str):
    """간단한 메시지 전송"""
    try:
        # 채팅 세션 존재 확인 (비즈니스 규칙)
        if not await self.chat_exists(chat_id):
            raise HandledException(ResponseCode.CHAT_SESSION_NOT_FOUND)
        
        # 메시지 검증 (비즈니스 규칙)
        if not message or len(message.strip()) == 0:
            raise HandledException(ResponseCode.CHAT_MESSAGE_INVALID)
        
        # Rate limit 확인 (비즈니스 규칙)
        if await self.is_rate_limited(chat_id):
            raise HandledException(ResponseCode.CHAT_RATE_LIMIT_EXCEEDED)
        
        # AI 응답 생성
        ai_response = await self.generate_ai_response(chat_id, message, user_id)
        return ai_response
        
    except HandledException:
        raise  # HandledException은 그대로 전파
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
```

### 3. 캐시 상태 조회 API (Router)

```python
# Router Layer (cache_router.py)
@router.get("/cache/status")
async def get_cache_status(
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
```

### 4. Redis 캐시 작업에서의 사용 (Service Layer)

```python
import redis
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode

async def cache_operation(redis_client, key: str, value: str):
    try:
        # Redis 작업 수행
        redis_client.set(key, value)
        return True
    except redis.exceptions.ResponseError as e:
        # Redis 명령어 에러 (잘못된 명령어, 데이터 타입 등)
        # Global Handler가 자동으로 처리하므로 별도 처리 불필요
        raise
    except redis.exceptions.ConnectionError as e:
        # Redis 연결 에러
        # Global Handler가 자동으로 처리하므로 별도 처리 불필요
        raise
    except redis.exceptions.TimeoutError as e:
        # Redis 타임아웃 에러
        # Global Handler가 자동으로 처리하므로 별도 처리 불필요
        raise
    except Exception as e:
        # 기타 예상치 못한 예외
        raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
```

### 5. 외부 API 호출에서의 사용 (Service Layer)

```python
import httpx
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode

async def call_external_api(url: str, data: dict):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
            
    except httpx.TimeoutException:
        raise HandledException(ResponseCode.EXTERNAL_SERVICE_TIMEOUT)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 503:
            raise HandledException(ResponseCode.EXTERNAL_SERVICE_UNAVAILABLE)
        else:
            raise HandledException(ResponseCode.EXTERNAL_SERVICE_ERROR, e=e)
    except Exception as e:
        raise HandledException(ResponseCode.EXTERNAL_SERVICE_ERROR, e=e)
```

## HTTP 상태 코드 매핑

시스템은 `ResponseCode`에 따라 자동으로 적절한 HTTP 상태 코드를 설정합니다:

### 4xx 클라이언트 에러 (400)
- 사용자 관련 에러 (-1201, -1202, -1203)
- 채팅 관련 에러 (-1301, -1302)
- 검증 관련 에러 (-1601, -1602, -1603)

### 429 Too Many Requests
- Rate limit 에러 (-1303)

### 5xx 서버 에러 (500)
- 데이터베이스 관련 에러 (-1401, -1402, -1403)
- 캐시 관련 에러 (-1501, -1502)
- 외부 서비스 관련 에러 (-1701, -1702, -1703)

### 커스텀 HTTP 상태 코드 사용

```python
# 404 Not Found
raise HandledException(
    ResponseCode.USER_NOT_FOUND, 
    http_status_code=404
)

# 401 Unauthorized
raise HandledException(
    ResponseCode.USER_INVALID_CREDENTIALS, 
    http_status_code=401
)
```

## 모범 사례

### 1. 예외 처리 계층 구조

```python
# Service Layer
async def business_logic():
    try:
        # 비즈니스 로직
        result = await some_operation()
        return result
    except HandledException:
        raise  # HandledException은 그대로 전파
    except Exception as e:
        # 예상치 못한 예외를 HandledException으로 변환
        raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)

# Controller Layer
@router.post("/users")
async def create_user(user_data: UserCreateRequest):
    try:
        result = user_service.create_user(user_data.dict())
        return CommonResponse(data=result)
    except HandledException as e:
        # Global exception handler가 자동으로 처리
        raise
```

### 2. 로깅과 함께 사용

```python
import logging
logger = logging.getLogger(__name__)

async def some_operation():
    try:
        # 작업 수행
        pass
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        raise HandledException(ResponseCode.OPERATION_FAILED, e=e)
```

### 3. 검증 로직에서 사용

```python
from pydantic import ValidationError

async def validate_user_data(data: dict):
    try:
        user = UserCreateRequest(**data)
        return user
    except ValidationError as e:
        raise HandledException(
            ResponseCode.VALIDATION_ERROR, 
            msg=f"Validation failed: {str(e)}"
        )
```

### 4. 데이터베이스 작업에서 사용

```python
from sqlalchemy.exc import SQLAlchemyError

async def database_operation():
    try:
        # DB 작업
        result = await db.execute(query)
        return result
    except SQLAlchemyError as e:
        raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
```

## 응답 형식

모든 에러는 다음과 같은 표준 형식으로 응답됩니다:

```json
{
    "timestamp": 1640995200000,
    "code": -1201,
    "message": "사용자를 찾을 수 없습니다.",
    "traceId": null,
    "data": null
}
```

## 디버깅 팁

1. **로그 확인**: 모든 예외는 자동으로 로그에 기록됩니다
2. **traceId 사용**: 추적을 위해 traceId를 활용하세요
3. **원본 예외 보존**: `e` 파라미터로 원본 예외를 전달하면 디버깅이 쉬워집니다
4. **HTTP 상태 코드 확인**: 클라이언트에서 적절한 HTTP 상태 코드를 받는지 확인하세요

## 새로운 ResponseCode 추가

새로운 에러 코드를 추가할 때는 다음 규칙을 따르세요:

1. **범위별 분류**: 비즈니스 도메인별로 코드 범위를 할당
2. **의미있는 메시지**: 사용자에게 이해하기 쉬운 메시지 작성
3. **문서화**: 새로운 코드를 사용법에 추가

```python
# 새로운 ResponseCode 추가 예시
class ResponseCode(Enum):
    # ... 기존 코드들 ...
    
    # NEW_SERVICE = (-1800 ~ -1899)
    NEW_SERVICE_ERROR = (-1801, "새로운 서비스 오류가 발생했습니다.")
```

## 🎯 실제 구현된 API들

### User API (사용자 관리)
- **Router**: `user_router.py` - 10개 엔드포인트
- **Service**: `user_service.py` - 비즈니스 로직 처리
- **Repository**: `user_crud.py` - 데이터베이스 작업

### Chat API (채팅 서비스)
- **Router**: `chat_router.py` - 10개 엔드포인트
- **Service**: `llm_chat_service.py` - AI 채팅 로직
- **Repository**: `chat_crud.py` - 채팅 데이터 관리

### Cache API (캐시 관리)
- **Router**: `cache_router.py` - 4개 엔드포인트
- **Service**: 직접 Redis 클라이언트 사용
- **Repository**: Redis 직접 접근

### 🔄 계층별 Exception 처리 흐름

```
Client Request
     ↓
Router Layer (예외 처리 없음, Service 예외 전파)
     ↓
Service Layer (비즈니스 로직 예외 처리)
     ↓
Repository Layer (데이터베이스 예외 처리)
     ↓
Global Exception Handler (최종 예외 처리)
     ↓
ErrorResponse (표준화된 응답)
```

### 📊 구현된 예외 코드

| 범위 | 예외 코드 | 설명 |
|------|-----------|------|
| **사용자** | -1201 ~ -1203 | 사용자 관련 예외 |
| **채팅** | -1301 ~ -1303 | 채팅 관련 예외 |
| **데이터베이스** | -1401 ~ -1403 | 데이터베이스 관련 예외 |
| **캐시** | -1501 ~ -1502 | 캐시 관련 예외 |
| **검증** | -1601 ~ -1603 | 입력 검증 예외 |
| **외부 서비스** | -1701 ~ -1703 | 외부 API 예외 |

이 가이드를 따라 일관성 있고 유지보수하기 쉬운 예외 처리 시스템을 구축하세요.

## 문제 해결

### ❓ 자주 묻는 질문

#### Q1: 새로운 API를 만들 때 예외 처리는 어떻게 해야 하나요?
**A:** 계층별 패턴을 따라주세요:
- **Router**: 예외 처리 없이 Service 호출만
- **Service**: 비즈니스 로직 예외 처리
- **Repository**: 데이터베이스 예외 처리

#### Q2: 어떤 ResponseCode를 사용해야 할지 모르겠어요
**A:** 다음 규칙을 따르세요:
- **사용자 관련**: `USER_*` (-1200~-1299)
- **채팅 관련**: `CHAT_*` (-1300~-1399)
- **데이터베이스**: `DATABASE_*` (-1400~-1499)
- **캐시**: `CACHE_*` (-1500~-1599)
- **검증**: `VALIDATION_*` (-1600~-1699)
- **외부 서비스**: `EXTERNAL_SERVICE_*` (-1700~-1799)

#### Q3: Service Layer에서 `DATABASE_QUERY_ERROR`를 사용해도 되나요?
**A:** ❌ **사용하지 마세요!** Service Layer에서는 구체적인 예외 타입을 모르므로 `UNDEFINED_ERROR`를 사용하세요.

#### Q4: 예외가 발생했는데 응답이 제대로 안 나와요
**A:** 다음을 확인하세요:
1. `main.py`에서 `set_global_exception_handlers(app)` 호출했는지
2. `HandledException`을 올바르게 raise했는지
3. Router에서 try-catch로 예외를 잡지 않았는지

### 🔧 디버깅 팁

#### 1. 로그 확인
```python
# 예외 발생 시 자동으로 로그가 출력됩니다
# 로그에서 다음 정보를 확인하세요:
# - 예외 타입
# - 요청 정보 (method, url, headers)
# - 예외 코드와 메시지
```

#### 2. 예외 처리 흐름 확인
```
1. Repository에서 SQLAlchemy 예외 발생
2. DATABASE_* HandledException으로 변환
3. Service Layer로 전파
4. Router Layer로 전파
5. Global Handler에서 ErrorResponse로 변환
```

#### 3. HTTP 상태 코드 확인
```python
# HandledException의 http_status_code 속성 확인
exception = HandledException(ResponseCode.USER_NOT_FOUND)
print(exception.http_status_code)  # 400
```

### 🚨 주의사항

1. **Router Layer에서 try-catch 사용 금지**
   ```python
   # ❌ 잘못된 예시
   try:
       user = user_service.create_user(...)
   except Exception as e:
       # 이렇게 하면 Global Handler가 작동하지 않습니다!
   
   # ✅ 올바른 예시
   user = user_service.create_user(...)  # 그대로 전파
   ```

2. **Service Layer에서 구체적인 예외 코드 사용 금지**
   ```python
   # ❌ 잘못된 예시
   except Exception as e:
       raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
   
   # ✅ 올바른 예시
   except Exception as e:
       raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
   ```

3. **Repository Layer에서 트랜잭션 롤백 필수**
   ```python
   try:
       # 데이터베이스 작업
   except Exception as e:
       self.db.rollback()  # 반드시 롤백!
       raise HandledException(...)
   ```

## 📊 구현 현황

### ✅ 완료된 기능

- **Exception 클래스**: `HandledException`, `UnHandledException`
- **ResponseCode**: 6개 카테고리, 20개 예외 코드
- **Global Exception Handler**: 자동 예외 처리 및 로깅
  - 애플리케이션 예외: `HandledException`, `UnHandledException`
  - HTTP 예외: `HTTPException`, `StarletteHTTPException`, `HTTPRequestValidationError`
  - Python 내장 예외: `ValueError`, `KeyError`, `ConnectionError`, `FileNotFoundError`
  - Redis 예외: `redis.exceptions.ResponseError`, `redis.exceptions.ConnectionError`, `redis.exceptions.TimeoutError`
  - 범용 예외: `Exception` (모든 예외 포괄)
- **HTTP 상태 코드 매핑**: 자동 상태 코드 설정
- **계층별 예외 처리**: Router → Service → Repository 패턴

### 🎯 구현된 API들

| API | Router | Service | Repository | 엔드포인트 | 예외 처리 |
|-----|--------|---------|------------|-----------|-----------|
| **User** | `user_router.py` | `user_service.py` | `user_crud.py` | 10개 | ✅ 완료 |
| **Chat** | `chat_router.py` | `llm_chat_service.py` | `chat_crud.py` | 10개 | ✅ 완료 |
| **Cache** | `cache_router.py` | 직접 Redis | Redis 직접 | 4개 | ✅ 완료 |

### 🔧 검증 완료

- **코드 일치성**: 가이드와 실제 코드 100% 일치
- **예외 처리 흐름**: Repository → Service → Router → Global Handler
- **HTTP 상태 코드**: 자동 매핑 정상 작동
- **로깅 시스템**: 예외 발생 시 자동 로깅
- **Redis 예외 처리**: Redis 관련 모든 예외 타입 자동 처리
- **스택 트레이스 로깅**: 개발자 디버깅을 위한 상세 로깅 (`exc_info=True`)

### 📚 가이드 문서

- **[Exception 처리 가이드](EXCEPTION_GUIDE.md)**: 계층별 Exception 처리 전략과 실제 구현 예시
- **[설정 가이드](CONFIG_GUIDE.md)**: Pydantic Settings 사용법
- **[로깅 가이드](LOGGING_GUIDE.md)**: 로깅 시스템 사용법
- **[캐시 제어 가이드](CACHE_CONTROL.md)**: Redis 캐시 사용법

---

**신규 개발자는 이 가이드를 따라 일관성 있는 예외 처리를 구현하세요!** 🚀
