# FastAPI Template

FastAPI 기반 AI 백엔드 템플릿 프로젝트입니다.


## 🚀 주요 기능

- **FastAPI**: 고성능 웹 프레임워크
- **Pydantic Settings**: 타입 안전한 설정 관리
- **Redis 캐싱**: 고성능 캐시 시스템
- **OpenAI 통합**: AI 채팅 서비스
- **PostgreSQL**: 관계형 데이터베이스
- **Docker 지원**: 컨테이너화된 배포
- **Kubernetes 지원**: K8s Ingress + ConfigMap 연동

## ⚙️ 설정 관리 (Pydantic Settings)

이 프로젝트는 **Pydantic Settings**를 사용하여 설정을 관리합니다.

### 🔧 환경변수 설정

로컬 개발을 위해 `.env` 파일을 생성하세요:

```bash
# .env 파일 생성
touch .env
```

#### **로그 설정 (로컬 개발 권장)**
```bash
# .env 파일에 추가
LOG_TO_FILE=true
LOG_DIR=./logs
LOG_FILE=app.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=7
APP_LOG_LEVEL=debug
SERVER_LOG_LEVEL=info
APP_DEBUG=true
```

#### **전체 설정 예시**
```bash
# Application Configuration
APP_VERSION=1.0.0
APP_LOCALE=ko
APP_DEBUG=true
APP_ROOT_PATH=  # 리버스 프록시 환경에서 사용 (예: /api, /v1)
# 로컬 개발: "" (직접 접근)
# 프로덕션: "/api" (API Gateway 환경)

# Logging Configuration (로컬 개발)
LOG_TO_FILE=true
LOG_DIR=./logs
LOG_FILE=app.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=7
APP_LOG_LEVEL=debug
SERVER_LOG_LEVEL=info

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_RELOAD=true

# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=chat_db
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Cache Configuration
CACHE_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 📁 설정 파일 구조

```
app/backend/
├── ai_backend/config/
│   └── simple_settings.py    # 통합 설정 클래스
├── .env                      # 로컬 개발용 환경변수 (선택사항)
└── env.*.example            # 환경별 설정 템플릿
```

### 🔧 설정 방법

#### 1. 로컬 개발 환경

**방법 1: .env 파일 사용 (권장)**
```bash
# .env 파일 생성
cp env.local.example .env

# .env 파일 편집
OPENAI_API_KEY=your_openai_api_key_here
CACHE_ENABLED=true
DATABASE_HOST=localhost
SERVER_PORT=8000
```

**방법 2: 환경변수 직접 설정**
```bash
export OPENAI_API_KEY=your_openai_api_key_here
export CACHE_ENABLED=true
export DATABASE_HOST=localhost
export SERVER_PORT=8000
```

#### 2. Docker 환경

```bash
# Docker Compose 사용
docker-compose up -d

# 또는 환경변수와 함께 실행
docker run -e OPENAI_API_KEY=your_key -e CACHE_ENABLED=true your-image
```

#### 3. Kubernetes 환경

**ConfigMap으로 설정 주입:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  OPENAI_API_KEY: "your_openai_api_key"
  CACHE_ENABLED: "true"
  DATABASE_HOST: "postgres-service"
  SERVER_PORT: "8000"
  REDIS_HOST: "redis-service"
```

### 📋 주요 설정 항목

| 설정 | 환경변수 | 기본값 | 설명 |
|------|----------|--------|------|
| **OpenAI** | | | |
| API Key | `OPENAI_API_KEY` | `""` | OpenAI API 키 (필수) |
| Model | `OPENAI_MODEL` | `gpt-3.5-turbo` | 사용할 모델 |
| Max Tokens | `OPENAI_MAX_TOKENS` | `1000` | 최대 토큰 수 |
| Temperature | `OPENAI_TEMPERATURE` | `0.7` | 생성 온도 |
| **서버** | | | |
| Host | `SERVER_HOST` | `0.0.0.0` | 서버 호스트 |
| Port | `SERVER_PORT` | `8000` | 서버 포트 |
| Debug | `SERVER_DEBUG` | `false` | 디버그 모드 |
| **데이터베이스** | | | |
| Host | `DATABASE_HOST` | `localhost` | DB 호스트 |
| Port | `DATABASE_PORT` | `5432` | DB 포트 |
| Name | `DATABASE_NAME` | `chat_db` | DB 이름 |
| Username | `DATABASE_USERNAME` | `postgres` | DB 사용자명 |
| Password | `DATABASE_PASSWORD` | `password` | DB 비밀번호 |
| **캐시** | | | |
| Enabled | `CACHE_ENABLED` | `true` | 캐시 활성화 |
| TTL Chat Messages | `CACHE_TTL_CHAT_MESSAGES` | `1800` | 채팅 메시지 TTL(초) |
| TTL User Chats | `CACHE_TTL_USER_CHATS` | `600` | 사용자 채팅 TTL(초) |
| **Redis** | | | |
| Host | `REDIS_HOST` | `localhost` | Redis 호스트 |
| Port | `REDIS_PORT` | `6379` | Redis 포트 |
| DB | `REDIS_DB` | `0` | Redis DB 번호 |
| Password | `REDIS_PASSWORD` | `None` | Redis 비밀번호 |

### 🔄 설정 우선순위

1. **환경변수** (최고 우선순위)
2. **.env 파일** (로컬 개발용)
3. **기본값** (최저 우선순위)

### ✅ 설정 테스트

```bash
# 설정 확인
python test_config.py

# 특정 환경변수로 테스트
OPENAI_API_KEY=test_key CACHE_ENABLED=true python test_config.py
```

### 🚨 주의사항

- **`.env` 파일이 없어도 에러가 나지 않습니다**
- **K8s 환경에서는 ConfigMap으로 환경변수를 주입하세요**
- **`OPENAI_API_KEY`는 필수 설정입니다**
- **설정 변경 후 애플리케이션 재시작이 필요합니다**

## 🛠️ 설치 및 실행

### 🚀 빠른 시작 (자동 설정)

```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd fastapi-template-master/app/backend

# 2. 환경 설정 (한 번만 실행)
chmod +x setup_python312.sh
./setup_python312.sh

# 3. 설정 파일 생성
cp env.local.example .env
# .env 파일을 편집하여 필요한 설정값 입력

# 4. 서버 실행
source venv/bin/activate
python -m uvicorn ai_backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 🔧 수동 설정

```bash
# Python 3.12 설치 (macOS)
brew install python@3.12

# 가상환경 생성
python3.12 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -e .

# 설정 파일 생성
cp env.local.example .env

# 애플리케이션 실행
python -m uvicorn ai_backend.main:app --reload
```

### 📋 환경 요구사항

- **Python**: 3.12 이상
- **pip**: 최신 버전
- **Redis**: 캐시용 (선택사항)
- **PostgreSQL**: 데이터베이스 (선택사항)

## 🚀 Kubernetes 배포

### K8s 환경에서의 배포

```bash
# ConfigMap 적용
kubectl apply -f k8s-configmap.yaml

# FastAPI 애플리케이션 배포
kubectl apply -f k8s-deployment.yaml

# Ingress 설정 (외부 접근)
kubectl apply -f k8s-ingress.yaml
```

### K8s 환경에서의 설정

- **ConfigMap**: 환경변수 주입
- **Ingress**: 외부 접근 및 라우팅
- **Service**: 내부 통신
- **Nginx 불필요**: Ingress Controller가 역할 대신

## 📚 더 자세한 정보

### 프로젝트 가이드

#### 🚀 핵심 가이드 (신규 개발자 필수)
- **[Exception 처리 가이드](EXCEPTION_GUIDE.md)** - 계층별 예외 처리 전략과 실제 구현 예시
- **[설정 가이드](CONFIG_GUIDE.md)** - Pydantic Settings 기반 설정 관리
- **[로깅 가이드](LOGGING_GUIDE.md)** - 일관성 있는 로깅 시스템 구현
- **[캐시 제어 가이드](CACHE_CONTROL.md)** - Redis 캐시 시스템 활용

#### 📊 가이드 특징
- **실제 코드 기반**: 모든 예시가 실제 구현과 100% 일치
- **신규 개발자 친화적**: 5분 만에 시작할 수 있는 빠른 시작 가이드
- **문제 해결 중심**: 자주 묻는 질문과 디버깅 팁 포함
- **구현 현황 제공**: 완료된 기능과 검증 상태 명시

### 외부 문서
- [Pydantic Settings 공식 문서](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Kubernetes ConfigMap 가이드](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Kubernetes Ingress 가이드](https://kubernetes.io/docs/concepts/services-networking/ingress/)
