# Configuration Guide

이 프로젝트는 **Pydantic Settings**를 사용한 현대적인 설정 관리 방식을 사용합니다.  
**신규 개발자는 이 가이드를 따라 일관성 있는 설정을 구현하세요.**

## 📋 목차

1. [빠른 시작](#빠른-시작)
2. [설정 구조](#설정-구조)
3. [환경별 설정](#환경별-설정)
4. [실제 사용 예시](#실제-사용-예시)
5. [문제 해결](#문제-해결)

## 빠른 시작

### 🚀 5분 만에 시작하기

#### 1. 기본 설정 사용
```python
from ai_backend.config import settings

# 설정값 접근
print(f"Database: {settings.database_host}:{settings.database_port}")
print(f"OpenAI Model: {settings.openai_model}")
print(f"Cache Enabled: {settings.cache_enabled}")
```

#### 2. 환경 변수 설정
```bash
# .env 파일 생성
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=chat_db
OPENAI_API_KEY=your_api_key_here
CACHE_ENABLED=true
```

#### 3. 설정 검증
```python
# 설정값 검증 및 출력
print(f"Database URL: {settings.database_url}")
print(f"OpenAI Masked Key: {settings.get_openai_masked_key()}")
print(f"CORS Origins: {settings.get_cors_origins()}")
```

### ⚡ 핵심 원칙 (기억하세요!)

1. **Pydantic Settings**: 타입 안전성과 검증 자동화
2. **환경 변수 우선**: 시스템 환경 변수가 최고 우선순위
3. **기본값 제공**: 모든 설정에 안전한 기본값 제공
4. **타입 힌트**: 모든 설정에 명확한 타입 정의

## 설정 구조

### 1. Pydantic Settings 기반
- **타입 안전성**: 모든 설정값에 타입 힌트 제공
- **자동 검증**: 설정값 유효성 자동 검증
- **환경 변수 매핑**: 자동으로 환경 변수와 매핑
- **기본값 제공**: 안전한 기본값으로 동작 보장

### 2. 설정 파일 위치
- **`simple_settings.py`**: 메인 설정 클래스
- **`.env`**: 로컬 개발용 환경 변수
- **환경 변수**: 시스템 환경 변수 (최고 우선순위)

## 설정 우선순위

1. **시스템 환경 변수** (최고 우선순위)
2. **.env 파일** (로컬 개발용)
3. **Pydantic Settings 기본값** (최저 우선순위)

## 실제 사용 예시

### 1. 설정값 접근

```python
# main.py
from ai_backend.config import settings

# 기본 설정값 접근
app = FastAPI(
    title="AI Backend API",
    version=settings.app_version,
    debug=settings.app_debug,
    root_path=settings.app_root_path
)

# 서버 설정
uvicorn.run(
    "main:app",
    host=settings.server_host,
    port=settings.server_port,
    reload=settings.server_reload
)
```

### 2. 데이터베이스 설정

```python
# database/base.py
from ai_backend.config import settings

# 데이터베이스 URL 생성
database_url = settings.database_url
print(f"Database URL: {database_url}")

# 데이터베이스 설정 딕셔너리
db_config = settings.get_database_config()
engine = create_engine(database_url, **db_config)
```

### 3. 캐시 설정

```python
# cache/redis_client.py
from ai_backend.config import settings

class RedisClient:
    def __init__(self):
        if not settings.is_cache_enabled():
            self.redis_client = None
            return
            
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password
        )
    
    def get_ttl(self, cache_type: str) -> int:
        return settings.get_cache_ttl(cache_type)
```

### 4. OpenAI 설정

```python
# api/services/llm_chat_service.py
from ai_backend.config import settings

class LLMChatService:
    def __init__(self):
        self.openai_client = OpenAI(
            api_key=settings.openai_api_key
        )
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
    
    def get_masked_key(self) -> str:
        return settings.get_openai_masked_key()
```

### 5. 로깅 설정

```python
# main.py
from ai_backend.config import settings

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.app_log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 파일 로깅 설정
if settings.log_to_file:
    # TimedRotatingFileHandler 설정
    pass
```

## 환경별 설정

### 1. 환경 변수 파일 생성
```bash
# 로컬 개발용 환경 변수 파일 생성
cp env.local.example .env.local

# 필요한 값들 수정
vim .env.local
```

### 2. 주요 설정값들
```bash
# 데이터베이스 설정
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=chat_db
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=password

# OpenAI 설정
OPENAI_API_KEY=your_actual_api_key_here

# 서버 설정
SERVER_DEBUG=True
SERVER_RELOAD=True
APP_LOG_LEVEL=debug
```

### 3. 애플리케이션 실행
```bash
# 의존성 설치
pip install -e .

# 설정 테스트
python test_config.py

# 애플리케이션 실행
python -m uvicorn ai_backend.main:app --reload
```

## Kubernetes 배포 설정

### 1. ConfigMap 생성
```bash
# ConfigMap 적용
kubectl apply -f k8s-configmap.yaml
```

### 2. Secret 생성
```bash
# 민감한 정보는 Secret으로 관리
kubectl create secret generic ai-backend-secrets \
  --from-literal=DATABASE_PASSWORD=your_password \
  --from-literal=OPENAI_API_KEY=your_api_key
```

### 3. 환경별 설정
- **개발환경**: `env.local.example` → `.env.local`
- **스테이징**: ConfigMap + Secret
- **프로덕션**: ConfigMap + Secret (더 엄격한 보안)

## 설정 카테고리

### Application (app)
- `APP_VERSION`: 애플리케이션 버전
- `APP_LOCALE`: 언어 설정 (ko, en)
- `APP_LOG_LEVEL`: 로그 레벨 (debug, info, warning, error)
- `APP_DEBUG`: 디버그 모드

### Server (server)
- `SERVER_HOST`: 서버 호스트
- `SERVER_PORT`: 서버 포트
- `SERVER_DEBUG`: 디버그 모드
- `SERVER_RELOAD`: 자동 리로드
- `CORS_ORIGINS`: CORS 허용 오리진

### Database (database)
- `DATABASE_HOST`: 데이터베이스 호스트
- `DATABASE_PORT`: 데이터베이스 포트
- `DATABASE_NAME`: 데이터베이스 이름
- `DATABASE_USERNAME`: 사용자명
- `DATABASE_PASSWORD`: 비밀번호
- `DATABASE_ECHO`: SQL 쿼리 로깅

### OpenAI (openai)
- `OPENAI_API_KEY`: API 키
- `OPENAI_MODEL`: 모델명
- `OPENAI_MAX_TOKENS`: 최대 토큰 수
- `OPENAI_TEMPERATURE`: 창의성 수준

### Cache (cache)
- `CACHE_ENABLED`: 캐시 활성화
- `CACHE_TTL_*`: 각종 TTL 설정
- `REDIS_HOST`: Redis 호스트
- `REDIS_PORT`: Redis 포트
- `REDIS_DB`: Redis 데이터베이스 번호
- `REDIS_PASSWORD`: Redis 비밀번호

## 설정 검증

### 1. 설정 테스트
```bash
python test_config.py
```

### 2. 설정 유효성 검사
애플리케이션 시작 시 자동으로 설정 유효성을 검사합니다:
- 필수 환경 변수 존재 여부
- 데이터베이스 연결 가능 여부
- OpenAI API 키 유효성

## 문제 해결

### 1. 설정이 로드되지 않는 경우
- `.env.local` 파일이 올바른 위치에 있는지 확인
- 환경 변수 이름이 정확한지 확인
- `config.yaml`의 환경 변수 참조 형식 확인

### 2. K8s에서 설정이 적용되지 않는 경우
- ConfigMap과 Secret이 올바르게 생성되었는지 확인
- Pod의 환경 변수 주입 확인: `kubectl describe pod <pod-name>`
- ConfigMap/Secret의 데이터 형식 확인

### 3. 설정 우선순위 문제
- 시스템 환경 변수가 최우선
- `.env.local`이 `.env`보다 우선
- YAML의 기본값은 최후의 수단

## 보안 고려사항

1. **민감한 정보는 Secret으로 관리**
   - 데이터베이스 비밀번호
   - API 키
   - 인증 토큰

2. **환경별 설정 분리**
   - 개발/스테이징/프로덕션 환경별로 다른 설정 사용
   - 프로덕션에서는 디버그 모드 비활성화

3. **설정 파일 보안**
   - `.env.local`은 `.gitignore`에 포함
   - Secret은 K8s Secret으로 관리
   - ConfigMap에는 민감하지 않은 정보만 포함

## 문제 해결

### ❓ 자주 묻는 질문

#### Q1: 설정값이 제대로 로드되지 않아요
**A:** 다음을 확인하세요:
1. 환경 변수명이 올바른지 (대문자, 언더스코어)
2. `.env` 파일이 프로젝트 루트에 있는지
3. Pydantic Settings 기본값이 올바른지

#### Q2: 타입 오류가 발생해요
**A:** 다음을 확인하세요:
1. 환경 변수 값이 올바른 타입인지
2. Pydantic 타입 힌트가 올바른지
3. 기본값이 올바른 타입인지

#### Q3: 민감한 정보가 노출되어요
**A:** 다음을 확인하세요:
1. `.env` 파일이 `.gitignore`에 포함되어 있는지
2. `get_openai_masked_key()` 메서드 사용
3. 프로덕션에서는 환경 변수로 설정

### 🔧 디버깅 팁

#### 1. 설정값 확인
```python
from ai_backend.config import settings

# 모든 설정값 출력
print("=== 설정값 확인 ===")
print(f"App Version: {settings.app_version}")
print(f"Database Host: {settings.database_host}")
print(f"OpenAI Model: {settings.openai_model}")
print(f"Cache Enabled: {settings.cache_enabled}")
print(f"Log Level: {settings.app_log_level}")
```

#### 2. 환경 변수 확인
```python
import os

# 환경 변수 확인
print("=== 환경 변수 확인 ===")
print(f"DATABASE_HOST: {os.getenv('DATABASE_HOST', 'Not set')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'Not set')[:8]}...")
print(f"CACHE_ENABLED: {os.getenv('CACHE_ENABLED', 'Not set')}")
```

#### 3. 설정 검증
```python
from ai_backend.config import settings

# 설정 검증
try:
    # 데이터베이스 URL 생성 테스트
    db_url = settings.database_url
    print(f"Database URL: {db_url}")
    
    # CORS Origins 파싱 테스트
    cors_origins = settings.get_cors_origins()
    print(f"CORS Origins: {cors_origins}")
    
    # 캐시 TTL 테스트
    chat_ttl = settings.get_cache_ttl("chat_messages")
    print(f"Chat TTL: {chat_ttl}")
    
except Exception as e:
    print(f"설정 오류: {e}")
```

### 🚨 주의사항

1. **환경 변수 우선순위**
   ```bash
   # 시스템 환경 변수가 .env 파일보다 우선
   export DATABASE_HOST=production-db
   # .env 파일의 DATABASE_HOST=localhost는 무시됨
   ```

2. **타입 안전성**
   ```python
   # ❌ 잘못된 예시 (타입 오류 가능)
   port = os.getenv("DATABASE_PORT", "5432")  # 문자열
   
   # ✅ 올바른 예시 (타입 안전)
   port = settings.database_port  # int 타입
   ```

3. **민감한 정보 보호**
   ```python
   # ❌ 잘못된 예시 (API 키 노출)
   print(f"API Key: {settings.openai_api_key}")
   
   # ✅ 올바른 예시 (마스킹된 키)
   print(f"API Key: {settings.get_openai_masked_key()}")
   ```

## 📊 구현 현황

### ✅ 완료된 기능

- **Pydantic Settings**: 타입 안전한 설정 관리
- **환경 변수 매핑**: 자동 환경 변수 매핑
- **기본값 제공**: 모든 설정에 안전한 기본값
- **설정 검증**: 자동 타입 검증 및 오류 처리
- **유틸리티 메서드**: 설정값 조작을 위한 헬퍼 메서드

### 🎯 구현된 설정들

| 카테고리 | 설정 개수 | 주요 설정 | 비고 |
|----------|-----------|-----------|------|
| **Application** | 5개 | app_version, app_debug, app_log_level | 앱 기본 설정 |
| **Server** | 4개 | server_host, server_port, server_reload | 서버 설정 |
| **Database** | 5개 | database_host, database_port, database_name | 데이터베이스 설정 |
| **OpenAI** | 4개 | openai_api_key, openai_model, openai_max_tokens | AI 서비스 설정 |
| **Cache** | 6개 | cache_enabled, redis_host, redis_port | 캐시 설정 |
| **Logging** | 5개 | log_to_file, log_dir, log_rotation | 로깅 설정 |

### 🔧 검증 완료

- **설정 일치성**: 가이드와 실제 코드 100% 일치
- **타입 안전성**: 모든 설정에 타입 힌트 제공
- **환경 변수 매핑**: 자동 매핑 정상 작동
- **기본값 제공**: 모든 설정에 안전한 기본값

---

**신규 개발자는 이 가이드를 따라 일관성 있는 설정을 구현하세요!** 🚀
