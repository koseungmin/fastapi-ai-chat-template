# LLM 제공자 가이드 (OpenAI vs Azure OpenAI)

## 개요

이제 시스템에서 **OpenAI**와 **Azure OpenAI** 두 가지 LLM 제공자를 지원합니다. 환경 변수 설정으로 쉽게 전환할 수 있습니다.

## 🚀 빠른 시작

### 1. 환경 변수 설정

`.env` 파일에서 `LLM_PROVIDER` 설정:

```bash
# OpenAI 사용
LLM_PROVIDER=openai

# Azure OpenAI 사용  
LLM_PROVIDER=azure_openai
```

### 2. OpenAI 설정 (기본값)

```bash
# .env 파일
LLM_PROVIDER=openai

# OpenAI 설정
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7
```

### 3. Azure OpenAI 설정

```bash
# .env 파일
LLM_PROVIDER=azure_openai

# Azure OpenAI 설정
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_MAX_TOKENS=1000
AZURE_OPENAI_TEMPERATURE=0.7
```

## 🔧 상세 설정

### 환경 변수 목록

| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `LLM_PROVIDER` | 사용할 LLM 제공자 (`openai` 또는 `azure_openai`) | `openai` | ✅ |
| `OPENAI_API_KEY` | OpenAI API 키 | - | OpenAI 사용 시 |
| `OPENAI_MODEL` | OpenAI 모델명 | `gpt-3.5-turbo` | ❌ |
| `OPENAI_MAX_TOKENS` | OpenAI 최대 토큰 수 | `1000` | ❌ |
| `OPENAI_TEMPERATURE` | OpenAI 온도 설정 | `0.7` | ❌ |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API 키 | - | Azure 사용 시 |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI 엔드포인트 | - | Azure 사용 시 |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure OpenAI 배포명 | - | Azure 사용 시 |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API 버전 | `2024-02-15-preview` | ❌ |
| `AZURE_OPENAI_MAX_TOKENS` | Azure OpenAI 최대 토큰 수 | `1000` | ❌ |
| `AZURE_OPENAI_TEMPERATURE` | Azure OpenAI 온도 설정 | `0.7` | ❌ |

## 🧪 테스트 방법

### 1. 자동 테스트 스크립트

```bash
# 테스트 스크립트 실행
python test_llm_providers.py
```

### 2. 수동 테스트

1. **환경 변수 설정**
   ```bash
   # OpenAI 테스트
   export LLM_PROVIDER=openai
   export OPENAI_API_KEY=your_key
   
   # Azure OpenAI 테스트
   export LLM_PROVIDER=azure_openai
   export AZURE_OPENAI_API_KEY=your_key
   export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   export AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
   ```

2. **서버 재시작**
   ```bash
   # 환경 변수 변경 후 서버 재시작 필요
   python main.py
   ```

3. **웹 브라우저 테스트**
   - `http://localhost:8000/llm_chat_client.html` 접속
   - 채팅을 통해 제공자 동작 확인

## 🏗️ 아키텍처

### 제공자 팩토리 패턴

```python
# LLM 제공자 팩토리
class LLMProviderFactory:
    @staticmethod
    def create_provider() -> BaseLLMProvider:
        provider_type = os.getenv("LLM_PROVIDER", "openai")
        
        if provider_type == "openai":
            return OpenAIProvider(...)
        elif provider_type == "azure_openai":
            return AzureOpenAIProvider(...)
        else:
            raise HandledException(...)
```

### 제공자 인터페이스

```python
class BaseLLMProvider:
    async def create_completion(self, messages: list, stream: bool = False):
        """LLM 응답 생성"""
        raise NotImplementedError
    
    async def create_title_completion(self, message: str):
        """채팅 제목 생성"""
        raise NotImplementedError
```

## 🔄 제공자 전환

### 런타임 전환

현재는 서버 재시작이 필요합니다. 향후 개선 예정:

```bash
# 1. 환경 변수 변경
export LLM_PROVIDER=azure_openai

# 2. 서버 재시작
python main.py

# 3. 테스트
python test_llm_providers.py
```

### 설정 파일 기반 전환

`.env` 파일 수정:

```bash
# OpenAI에서 Azure OpenAI로 전환
sed -i 's/LLM_PROVIDER=openai/LLM_PROVIDER=azure_openai/' .env

# 서버 재시작
python main.py
```

## 🐛 문제 해결

### 1. OpenAI 연결 오류

```
❌ OpenAI API error: Invalid API key
```

**해결 방법:**
- `OPENAI_API_KEY` 확인
- API 키가 유효한지 확인
- 결제 정보 확인

### 2. Azure OpenAI 연결 오류

```
❌ Azure OpenAI API error: 401 Unauthorized
```

**해결 방법:**
- `AZURE_OPENAI_API_KEY` 확인
- `AZURE_OPENAI_ENDPOINT` 형식 확인
- `AZURE_OPENAI_DEPLOYMENT_NAME` 확인
- Azure 포털에서 배포 상태 확인

### 3. 제공자 설정 오류

```
❌ Unsupported LLM provider: invalid_provider
```

**해결 방법:**
- `LLM_PROVIDER` 값 확인 (`openai` 또는 `azure_openai`)
- 대소문자 구분 없음

### 4. 환경 변수 누락

```
❌ OpenAI API key is required
```

**해결 방법:**
- `.env` 파일에서 필수 환경 변수 확인
- 서버 재시작

## 📊 성능 비교

| 항목 | OpenAI | Azure OpenAI |
|------|--------|--------------|
| 응답 속도 | 빠름 | 빠름 |
| 안정성 | 높음 | 높음 |
| 비용 | 사용량 기반 | 사용량 기반 |
| 지역 제한 | 있음 | 없음 |
| 커스터마이징 | 제한적 | 높음 |

## 🔮 향후 계획

### 1. 추가 제공자 지원
- Google Gemini
- Anthropic Claude
- 로컬 모델 (Ollama)

### 2. 동적 제공자 전환
- 런타임 제공자 변경
- 제공자별 부하 분산
- 자동 failover

### 3. 모니터링 및 로깅
- 제공자별 성능 메트릭
- 사용량 추적
- 에러 모니터링

## 💡 팁

### 1. 개발 환경 설정
```bash
# 로컬 개발용 OpenAI
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_dev_key
```

### 2. 프로덕션 환경 설정
```bash
# 프로덕션용 Azure OpenAI
export LLM_PROVIDER=azure_openai
export AZURE_OPENAI_API_KEY=your_prod_key
export AZURE_OPENAI_ENDPOINT=https://prod-resource.openai.azure.com/
```

### 3. A/B 테스트
```bash
# 서버 A: OpenAI
export LLM_PROVIDER=openai

# 서버 B: Azure OpenAI  
export LLM_PROVIDER=azure_openai
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. 환경 변수 설정
2. API 키 유효성
3. 네트워크 연결
4. 서버 로그

자세한 로그는 `./logs/app.log`에서 확인할 수 있습니다.
