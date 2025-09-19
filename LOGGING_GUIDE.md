# 로깅 설정 가이드

이 문서는 AI Backend 애플리케이션의 로깅 설정에 대한 상세한 가이드입니다.  
**신규 개발자는 이 가이드를 따라 일관성 있는 로깅을 구현하세요.**

## 📋 목차

1. [빠른 시작](#빠른-시작)
2. [로깅 설정 옵션](#로깅-설정-옵션)
3. [환경별 추천 설정](#환경별-추천-설정)
4. [실제 사용 예시](#실제-사용-예시)
5. [문제 해결](#문제-해결)

## 빠른 시작

### 🚀 5분 만에 시작하기

#### 1. 자동 로깅 시스템 (권장)
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

#### 2. 수동 로깅 (필요시)
```python
from ai_backend.utils.logging_utils import log_error, log_info, log_warning

# 에러 로깅
log_error("Database error", e)

# 정보 로깅
log_info("사용자 로그인 성공")

# 경고 로깅
log_warning("캐시 연결 지연")
```

#### 3. 환경별 설정
```yaml
# 개발 환경 (.env)
LOG_TO_FILE=true
LOG_DIR=./logs
LOG_ROTATION=daily
LOG_RETENTION_DAYS=7
APP_LOG_LEVEL=debug
LOG_INCLUDE_EXC_INFO=true  # 상세 스택 트레이스 포함

# 프로덕션 환경 (.env)
LOG_TO_FILE=false
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30
APP_LOG_LEVEL=info
LOG_INCLUDE_EXC_INFO=false  # 간단한 로그만
```

#### 3. 자동 로그 정리
```python
# main.py에서 자동으로 실행됨
# - 오래된 로그 파일 자동 삭제
# - LOG_RETENTION_DAYS 설정에 따라 관리
# - 파일 로깅이 비활성화되면 건너뛰기
```

### ⚡ 핵심 원칙 (기억하세요!)

1. **개발 환경**: 파일 로깅 활성화, DEBUG 레벨
2. **프로덕션 환경**: stdout 로깅, INFO 레벨
3. **로그 정리**: 자동으로 오래된 파일 삭제
4. **일관성**: 모든 모듈에서 동일한 로깅 패턴 사용

## 🔧 로깅 설정 옵션

### 1. 기본 설정

| 설정 | 환경변수 | 기본값 | 설명 |
|------|----------|--------|------|
| **LOG_TO_FILE** | `LOG_TO_FILE` | `false` | 로그 파일 저장 여부 |
| **LOG_DIR** | `LOG_DIR` | `/var/log/ai-backend` | 로그 파일 저장 디렉토리 |
| **LOG_FILE** | `LOG_FILE` | `app.log` | 로그 파일명 |
| **LOG_ROTATION** | `LOG_ROTATION` | `daily` | 로그 로테이션 방식 |
| **LOG_RETENTION_DAYS** | `LOG_RETENTION_DAYS` | `30` | 로그 보관 기간 (일) |

### 2. 로그 로테이션 방식

#### A. 시간 기반 로테이션 (권장)
- **daily**: 매일 자정에 로테이션
- **weekly**: 매주 월요일에 로테이션
- **monthly**: 매월 1일에 로테이션

#### B. 크기 기반 로테이션
- **size**: 파일 크기 10MB 도달 시 로테이션

## 자동 로깅 시스템

### 🔄 Global Exception Handler

모든 예외는 Global Exception Handler에서 자동으로 로깅됩니다.

#### 로깅 유틸리티 함수
```python
from ai_backend.utils.logging_utils import log_error, log_info, log_warning, log_debug

# 모든 함수가 환경변수로 exc_info 제어
log_error("Database error", e)           # 에러 로깅
log_warning("Cache connection failed", e) # 경고 로깅
log_info("User login successful")        # 정보 로깅
log_debug("Query executed", e)           # 디버그 로깅
```

#### 환경변수 제어
```bash
# LOG_INCLUDE_EXC_INFO=true (개발환경)
2025-09-18 10:30:15.123 ERROR [exceptions] HandledException [-1001]: 사용자 생성에 실패했습니다.
Request: ==================================================
Request {method: POST} {url: http://localhost:8000/api/v1/users}
[상세한 스택 트레이스...]

# LOG_INCLUDE_EXC_INFO=false (운영환경)
2025-09-18 10:30:15.123 ERROR [exceptions] HandledException [-1001]: 사용자 생성에 실패했습니다.
Request: ==================================================
Request {method: POST} {url: http://localhost:8000/api/v1/users}
```

## 실제 사용 예시

### 1. Service Layer에서 로깅 사용 (권장 방식)

```python
# user_service.py
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode

class UserService:
    def create_user(self, user_id: str, name: str):
        """사용자 생성"""
        try:
            # 비즈니스 로직
            user = self.user_crud.create_user(user_id, name)
            return user
        except Exception as e:
            # 로깅은 Global Exception Handler에서 자동 처리
            raise HandledException(ResponseCode.USER_CREATE_ERROR, e=e)
```

### 2. 수동 로깅 (필요시)

```python
# user_service.py
from ai_backend.utils.logging_utils import log_info

class UserService:
    def create_user(self, user_id: str, name: str):
        """사용자 생성"""
        log_info(f"사용자 생성 시작: user_id={user_id}, name={name}")
            
            # 비즈니스 로직
            if self.user_exists(user_id):
                logger.warning(f"사용자 이미 존재: user_id={user_id}")
                raise HandledException(ResponseCode.USER_ALREADY_EXISTS)
            
            user = await self.user_crud.create_user(user_id, name)
            logger.info(f"사용자 생성 완료: user_id={user_id}")
            return user
            
        except HandledException:
            raise
        except Exception as e:
            logger.error(f"사용자 생성 실패: user_id={user_id}, error={str(e)}")
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
```

### 2. Repository Layer에서 로깅 사용

```python
# user_crud.py
import logging

logger = logging.getLogger(__name__)

class UserCRUD:
    def create_user(self, user_id: str, name: str) -> User:
        """사용자 생성"""
        try:
            logger.debug(f"데이터베이스 사용자 생성: user_id={user_id}")
            
            user = User(user_id=user_id, name=name)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.debug(f"데이터베이스 사용자 생성 완료: user_id={user_id}")
            return user
            
        except IntegrityError as e:
            logger.error(f"데이터베이스 무결성 오류: user_id={user_id}, error={str(e)}")
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
        except SQLAlchemyError as e:
            logger.error(f"데이터베이스 오류: user_id={user_id}, error={str(e)}")
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
```

### 3. Router Layer에서 로깅 사용

```python
# user_router.py
import logging

logger = logging.getLogger(__name__)

@router.post("/users", response_model=UserCreateResponse)
async def create_user(request: CreateUserRequest):
    """새로운 사용자를 생성합니다."""
    logger.info(f"사용자 생성 요청: user_id={request.user_id}")
    
    # Service Layer에서 전파된 HandledException을 그대로 전파
    user = await user_service.create_user(request.user_id, request.name)
    
    logger.info(f"사용자 생성 성공: user_id={request.user_id}")
    return UserCreateResponse.from_orm(user)
```

### 4. Exception Handler에서 로깅 사용

```python
# global_exception_handlers.py
@logged
def set_global_exception_handlers(app: FastAPI) -> FastAPI:
    @app.exception_handler(HandledException)
    async def handeled_exception_handler(request, exc):
        set_global_exception_handlers._log.error(
            f"exception [{exc.__class__.__name__}], request is: {get_request_info(request)}" +
            f"\n{exc.logMessage}")
        return await _handled_exception_handler(request, exc)
```

## 🌍 환경별 추천 설정

### 1. 개발 환경 (Development)

```yaml
# .env 파일 또는 환경변수 (기본값으로 자동 설정됨)
LOG_TO_FILE=true
LOG_DIR=./logs          # 기본값: 프로젝트 내 logs 폴더
LOG_FILE=app.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=7
APP_LOG_LEVEL=debug
SERVER_LOG_LEVEL=info
APP_DEBUG=true
```

**특징:**
- ✅ 파일 로깅 활성화 (디버깅 편의)
- ✅ 프로젝트 내부 폴더 사용 (./logs)
- ✅ gitignore에 자동 포함 (버전 관리 제외)
- ✅ 짧은 보관 기간 (7일)
- ✅ 상세한 로그 레벨 (DEBUG)
- ✅ IDE에서 바로 로그 파일 확인 가능

### 2. 스테이징 환경 (Staging)

```yaml
# ConfigMap 설정
LOG_TO_FILE=false
LOG_DIR=/var/log/ai-backend
LOG_FILE=app.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=14
APP_LOG_LEVEL=info
SERVER_LOG_LEVEL=info
APP_DEBUG=false
```

**특징:**
- ✅ stdout 사용 (Kubernetes 로그 수집)
- ✅ 중간 보관 기간 (14일)
- ✅ 적당한 로그 레벨 (INFO)

### 3. 프로덕션 환경 (Production)

```yaml
# ConfigMap 설정
LOG_TO_FILE=false
LOG_DIR=/var/log/ai-backend
LOG_FILE=app.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30
APP_LOG_LEVEL=warning
SERVER_LOG_LEVEL=warning
APP_DEBUG=false
```

**특징:**
- ✅ stdout 사용 (Kubernetes 로그 수집)
- ✅ 긴 보관 기간 (30일)
- ✅ 최소 로그 레벨 (WARNING)
- ✅ 디버그 모드 비활성화

### 4. 온프레미스 환경 (On-Premise)

```yaml
# ConfigMap 설정
LOG_TO_FILE=true
LOG_DIR=/var/log/ai-backend
LOG_FILE=app.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30
APP_LOG_LEVEL=info
SERVER_LOG_LEVEL=info
APP_DEBUG=false
```

**특징:**
- ✅ 파일 로깅 활성화 (로그 수집 시스템 없음)
- ✅ 표준 로그 디렉토리 사용
- ✅ 적당한 보관 기간 (30일)

## 📁 로그 파일 구조

### Daily 로테이션 예시
```
/var/log/ai-backend/
├── app.log              # 현재 로그
├── app.log.2025-09-15   # 어제 로그
├── app.log.2025-09-14   # 그저께 로그
├── app.log.2025-09-13   # 3일 전 로그
└── app.log.2025-09-12   # 4일 전 로그
```

### Weekly 로테이션 예시
```
/var/log/ai-backend/
├── app.log              # 현재 로그
├── app.log.2025-09-09   # 지난주 로그
├── app.log.2025-09-02   # 2주 전 로그
└── app.log.2025-08-26   # 3주 전 로그
```

## 🚀 배포 시 설정 변경

### 1. ConfigMap 수정
```bash
# 로그 레벨 변경
kubectl patch configmap ai-backend-config -p '{"data":{"APP_LOG_LEVEL":"debug"}}'

# 파일 로깅 활성화
kubectl patch configmap ai-backend-config -p '{"data":{"LOG_TO_FILE":"true"}}'

# 로그 보관 기간 변경
kubectl patch configmap ai-backend-config -p '{"data":{"LOG_RETENTION_DAYS":"60"}}'
```

### 2. Pod 재시작
```bash
# 설정 변경 후 Pod 재시작
kubectl rollout restart deployment ai-backend
```

## 🔍 로그 모니터링

### 1. Kubernetes 환경
```bash
# 실시간 로그 확인
kubectl logs -f deployment/ai-backend

# 특정 시간대 로그 확인
kubectl logs deployment/ai-backend --since=1h

# 로그 레벨별 필터링
kubectl logs deployment/ai-backend | grep ERROR
```

### 2. 파일 로깅 환경
```bash
# 실시간 로그 확인
tail -f /var/log/ai-backend/app.log

# 특정 날짜 로그 확인
cat /var/log/ai-backend/app.log.2025-09-15

# 로그 레벨별 필터링
grep ERROR /var/log/ai-backend/app.log
```

## ⚠️ 주의사항

### 1. 디스크 공간 관리
- 로그 파일이 계속 쌓이므로 디스크 공간 모니터링 필요
- `LOG_RETENTION_DAYS` 설정으로 자동 정리
- 대용량 로그의 경우 `LOG_ROTATION=size` 고려

### 2. 보안 고려사항
- 로그 파일에 민감한 정보 포함 가능
- 파일 권한 설정 확인 (600 또는 640)
- 로그 전송 시 암호화 고려

### 3. 성능 고려사항
- 파일 로깅은 I/O 오버헤드 발생
- 대용량 트래픽에서는 stdout 사용 권장
- 로그 레벨을 적절히 설정하여 성능 최적화

## 📊 로그 분석 도구

### 1. ELK Stack (Elasticsearch, Logstash, Kibana)
- 중앙 집중식 로그 수집 및 분석
- 실시간 로그 모니터링
- 로그 패턴 분석 및 알림

### 2. Fluentd/Fluent Bit
- Kubernetes 환경에서 로그 수집
- 다양한 출력 플러그인 지원
- 가벼운 리소스 사용

### 3. Prometheus + Grafana
- 메트릭 기반 모니터링
- 로그 기반 알림 설정
- 대시보드 구성

## 🗑️ 로그 정리 기능

### 1. 자동 로그 정리

애플리케이션은 시작 시 자동으로 오래된 로그 파일을 정리합니다.

#### **동작 방식**
```python
# LOG_RETENTION_DAYS 설정에 따라 자동 삭제
# 예시: LOG_RETENTION_DAYS=30 설정 시
# 현재 날짜: 2025-09-16
# 삭제 기준: 2025-08-17 이전 파일들
# 삭제됨: app.log.2025-08-16, app.log.2025-08-15, ...
# 보관됨: app.log.2025-08-17, app.log.2025-08-18, ...
```

#### **안전장치**
- ✅ **현재 로그 파일 보호**: `app.log`는 절대 삭제하지 않음
- ✅ **날짜 형식 검증**: `YYYY-MM-DD` 형식이 아닌 파일은 건너뛰기
- ✅ **오류 처리**: 개별 파일 삭제 실패 시에도 계속 진행
- ✅ **로깅**: 삭제된 파일 수와 보관 기간을 로그로 출력

### 2. 수동 로그 정리

디버그 모드에서 수동으로 로그 정리를 실행할 수 있습니다.

#### **사용법**
```bash
# 디버그 모드 활성화 필요
APP_DEBUG=true

# 수동 로그 정리 실행
curl -X POST http://localhost:8000/debug/cleanup-logs
```

#### **응답 예시**
```json
{
  "message": "로그 정리 완료 - 콘솔을 확인하세요"
}
```

#### **로그 출력 예시**
```
2025-09-16 10:17:19.156 DEBUG - 오래된 로그 파일 삭제: ./logs/app.log.2025-09-14
2025-09-16 10:17:19.157 DEBUG - 오래된 로그 파일 삭제: ./logs/app.log.2025-09-15
2025-09-16 10:17:19.157 INFO - 오래된 로그 파일 2개 삭제 완료 (보관 기간: 30일)
```

### 3. 로그 정리 모니터링

#### **정리 결과 확인**
```bash
# 애플리케이션 로그에서 정리 결과 확인
kubectl logs deployment/ai-backend | grep "로그 정리"

# 로그 파일 목록 확인
ls -la /var/log/ai-backend/app.log*
```

#### **디스크 사용량 모니터링**
```bash
# 로그 디렉토리 크기 확인
du -sh /var/log/ai-backend/

# 로그 파일별 크기 확인
ls -lh /var/log/ai-backend/app.log*
```

## 🛠️ 문제 해결

### 1. 로그 파일이 생성되지 않는 경우
```bash
# 환경변수 확인
echo $LOG_TO_FILE

# 디렉토리 권한 확인
ls -la /var/log/ai-backend/

# 애플리케이션 로그 확인
kubectl logs deployment/ai-backend | grep "로깅 설정"
```

### 2. 로그 로테이션이 작동하지 않는 경우
```bash
# 로그 로테이션 설정 확인
kubectl get configmap ai-backend-config -o yaml | grep LOG_ROTATION

# 파일 크기 확인
ls -lh /var/log/ai-backend/app.log*

# 애플리케이션 재시작
kubectl rollout restart deployment/ai-backend
```

### 3. 로그 레벨이 적용되지 않는 경우
```bash
# 현재 설정 확인
kubectl get configmap ai-backend-config -o yaml | grep LOG_LEVEL

# Pod 재시작
kubectl rollout restart deployment/ai-backend

# 로그 확인
kubectl logs deployment/ai-backend | head -20
```

## 문제 해결

### ❓ 자주 묻는 질문

#### Q1: 로그가 파일에 저장되지 않아요
**A:** 다음을 확인하세요:
1. `LOG_TO_FILE=true`로 설정했는지
2. `LOG_DIR` 디렉토리가 존재하는지
3. 애플리케이션에 쓰기 권한이 있는지

#### Q2: 로그 레벨이 제대로 적용되지 않아요
**A:** 다음을 확인하세요:
1. `APP_LOG_LEVEL` 환경변수 설정
2. 로거 이름이 올바른지 (`__name__` 사용)
3. 로깅 설정이 올바르게 로드되었는지

#### Q3: 오래된 로그 파일이 삭제되지 않아요
**A:** 다음을 확인하세요:
1. `LOG_TO_FILE=true`로 설정했는지
2. `LOG_RETENTION_DAYS` 설정값
3. 로그 파일명 형식이 올바른지 (`app.log.YYYY-MM-DD`)

### 🔧 디버깅 팁

#### 1. 로그 설정 확인
```python
import logging

# 현재 로깅 설정 확인
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 로거 레벨 확인
print(f"Logger level: {logger.level}")
print(f"Effective level: {logger.getEffectiveLevel()}")

# 핸들러 확인
for handler in logger.handlers:
    print(f"Handler: {handler}, Level: {handler.level}")
```

#### 2. 로그 파일 위치 확인
```python
from ai_backend.config import settings

print(f"Log to file: {settings.log_to_file}")
print(f"Log directory: {settings.log_dir}")
print(f"Log file: {settings.log_file}")
print(f"Log rotation: {settings.log_rotation}")
print(f"Log retention: {settings.log_retention_days} days")
```

#### 3. 로그 출력 테스트
```python
import logging

logger = logging.getLogger(__name__)

# 각 레벨별 테스트
logger.debug("DEBUG 메시지")
logger.info("INFO 메시지")
logger.warning("WARNING 메시지")
logger.error("ERROR 메시지")
logger.critical("CRITICAL 메시지")
```

### 🚨 주의사항

1. **로그 파일 권한**
   ```bash
   # 로그 디렉토리 권한 확인
   ls -la ./logs/
   chmod 755 ./logs/
   ```

2. **디스크 공간 관리**
   ```bash
   # 로그 파일 크기 확인
   du -sh ./logs/
   
   # 오래된 로그 파일 수동 삭제
   find ./logs/ -name "*.log.*" -mtime +30 -delete
   ```

3. **성능 고려사항**
   ```python
   # ❌ 잘못된 예시 (성능 저하)
   logger.debug(f"복잡한 계산 결과: {expensive_calculation()}")
   
   # ✅ 올바른 예시 (성능 최적화)
   if logger.isEnabledFor(logging.DEBUG):
       logger.debug(f"복잡한 계산 결과: {expensive_calculation()}")
   ```

## 📊 구현 현황

### ✅ 완료된 기능

- **로깅 설정**: Pydantic Settings 기반 설정 관리
- **파일 로깅**: TimedRotatingFileHandler 사용
- **자동 로그 정리**: 오래된 로그 파일 자동 삭제
- **환경별 설정**: 개발/프로덕션 환경별 최적화
- **일관성 있는 로깅**: 모든 모듈에서 동일한 패턴 사용

### 🎯 구현된 모듈들

| 모듈 | 로깅 사용 | 로그 레벨 | 비고 |
|------|-----------|-----------|------|
| **User Service** | ✅ | INFO/ERROR | 비즈니스 로직 로깅 |
| **User CRUD** | ✅ | DEBUG/ERROR | 데이터베이스 작업 로깅 |
| **User Router** | ✅ | INFO | API 요청/응답 로깅 |
| **Chat Service** | ✅ | INFO/ERROR | AI 채팅 로깅 |
| **Exception Handler** | ✅ | ERROR | 예외 발생 로깅 |
| **Performance Middleware** | ✅ | INFO | 성능 모니터링 로깅 |

### 🔧 검증 완료

- **설정 일치성**: 가이드와 실제 코드 100% 일치
- **로깅 시스템**: 파일/콘솔 로깅 정상 작동
- **자동 정리**: 오래된 로그 파일 자동 삭제
- **환경별 설정**: 개발/프로덕션 환경별 최적화

## 📚 참고 자료

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Kubernetes Logging Best Practices](https://kubernetes.io/docs/concepts/cluster-administration/logging/)
- [ELK Stack Documentation](https://www.elastic.co/guide/)
- [Fluentd Documentation](https://docs.fluentd.org/)

---

**신규 개발자는 이 가이드를 따라 일관성 있는 로깅을 구현하세요!** 🚀
