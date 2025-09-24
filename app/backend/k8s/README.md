# AI Backend Kubernetes Deployment

이 디렉토리는 AI Backend FastAPI 애플리케이션을 Kubernetes에 배포하기 위한 모든 리소스를 포함합니다.

## 파일 구조

```
k8s/
├── README.md                    # 이 파일
├── kustomization.yaml          # Kustomize 설정
├── configmap.yaml              # 애플리케이션 설정
├── secret.yaml                 # 민감한 정보 (패스워드, API 키)
├── persistent-volume.yaml      # 영구 저장소 (PV, PVC)
├── deployment.yaml             # 애플리케이션 배포
├── service.yaml                # 서비스 노출
└── ingress.yaml                # 외부 접근 (HTTP/HTTPS)
```

## 배포 전 준비사항

### 1. Docker 이미지 빌드

```bash
# 프로젝트 루트에서
cd app/backend
docker build -t ai-backend:latest .
```

### 2. 시크릿 설정

`secret.yaml` 파일에서 다음 값들을 실제 값으로 변경하세요:

```bash
# 데이터베이스 패스워드
echo -n "your-actual-db-password" | base64

# OpenAI API 키
echo -n "sk-your-actual-openai-api-key" | base64

# Azure OpenAI API 키
echo -n "your-actual-azure-openai-api-key" | base64

# Redis 패스워드 (선택사항)
echo -n "your-actual-redis-password" | base64
```

### 3. 설정 파일 수정

`configmap.yaml`에서 다음 설정들을 환경에 맞게 수정하세요:

- `CORS_ORIGINS`: 허용할 도메인들
- `DATABASE_HOST`: 데이터베이스 호스트 (예: `postgres-service`)
- `REDIS_HOST`: Redis 호스트 (예: `redis-service`)
- `LLM_PROVIDER`: LLM 제공자 (`openai` 또는 `azure_openai`)
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI 엔드포인트 URL
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Azure OpenAI 배포 이름

### 4. Ingress 설정

`ingress.yaml`에서 도메인을 실제 도메인으로 변경하세요:

```yaml
- host: api.yourdomain.com  # 실제 도메인으로 변경
```

## 배포 방법

### 환경별 배포 (권장)

#### Development 환경
```bash
# Development 환경 배포
kubectl apply -k overlays/development/

# 또는 개별 리소스 배포
kubectl apply -f overlays/development/configmap-patch.yaml
kubectl apply -f overlays/development/deployment-patch.yaml
```

#### Production 환경
```bash
# Production 환경 배포
kubectl apply -k overlays/production/

# 또는 개별 리소스 배포
kubectl apply -f overlays/production/configmap-patch.yaml
kubectl apply -f overlays/production/deployment-patch.yaml
```

### 방법 1: kubectl 사용

```bash
# 모든 리소스 배포
kubectl apply -f .

# 개별 리소스 배포
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f persistent-volume.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
```

### 방법 2: Kustomize 사용

```bash
# Kustomize로 배포
kubectl apply -k .

# 특정 환경으로 배포 (예: staging)
kubectl apply -k overlays/staging/
```

## 배포 확인

```bash
# Pod 상태 확인
kubectl get pods -l app=ai-backend

# 서비스 확인
kubectl get services -l app=ai-backend

# Ingress 확인
kubectl get ingress -l app=ai-backend

# 로그 확인
kubectl logs -l app=ai-backend -f

# 포트 포워딩 (로컬 테스트)
kubectl port-forward svc/ai-backend-service 8000:8000
```

## 헬스 체크

애플리케이션이 정상적으로 배포되었는지 확인:

```bash
# Pod 내부에서 헬스 체크
kubectl exec -it <pod-name> -- curl http://localhost:8000/health

# 서비스를 통한 헬스 체크
kubectl port-forward svc/ai-backend-service 8000:8000
curl http://localhost:8000/health
```

## 스케일링

```bash
# 레플리카 수 증가
kubectl scale deployment ai-backend-deployment --replicas=3

# 자동 스케일링 설정 (HPA가 설치된 경우)
kubectl autoscale deployment ai-backend-deployment --cpu-percent=70 --min=2 --max=10
```

## 업데이트

```bash
# 새로운 이미지로 업데이트
kubectl set image deployment/ai-backend-deployment ai-backend=ai-backend:v1.1.0

# 롤백
kubectl rollout undo deployment/ai-backend-deployment
```

## 트러블슈팅

### Pod가 시작되지 않는 경우

```bash
# Pod 상세 정보 확인
kubectl describe pod <pod-name>

# Pod 로그 확인
kubectl logs <pod-name>
```

### 서비스 연결 문제

```bash
# 서비스 엔드포인트 확인
kubectl get endpoints ai-backend-service

# DNS 확인
kubectl exec -it <pod-name> -- nslookup ai-backend-service
```

### Ingress 문제

```bash
# Ingress 컨트롤러 확인
kubectl get pods -n ingress-nginx

# Ingress 상세 정보
kubectl describe ingress ai-backend-ingress
```

## 리소스 정리

```bash
# 모든 리소스 삭제
kubectl delete -f .

# 또는 Kustomize 사용
kubectl delete -k .
```

## 보안 고려사항

1. **시크릿 관리**: 실제 운영 환경에서는 Kubernetes Secrets 대신 외부 시크릿 관리 도구 사용을 고려하세요.
2. **네트워크 정책**: 필요에 따라 NetworkPolicy를 설정하여 Pod 간 통신을 제한하세요.
3. **RBAC**: 적절한 Role-Based Access Control을 설정하세요.
4. **Pod Security Standards**: Pod Security Standards를 적용하세요.

## 모니터링

배포 후 다음 모니터링 도구들의 설정을 고려하세요:

- **Prometheus + Grafana**: 메트릭 수집 및 시각화
- **ELK Stack**: 로그 수집 및 분석
- **Jaeger**: 분산 추적
- **Kubernetes Dashboard**: 클러스터 관리 UI
