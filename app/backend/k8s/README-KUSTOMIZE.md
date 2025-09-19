# Kustomize 사용 가이드

## Kustomize란?

**Kustomize**는 Kubernetes의 공식 도구로, YAML 파일들을 커스터마이징하고 관리하는 도구입니다.

- "Kustomize" = "Customize"의 K 버전 (Kubernetes를 위한 커스터마이징)
- 여러 환경(개발, 스테이징, 프로덕션)에서 동일한 기본 설정을 재사용하면서 환경별 차이점만 관리

## 디렉토리 구조

```
k8s/
├── base/                           # 기본 설정
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ...
└── overlays/                       # 환경별 오버레이
    ├── development/
    │   ├── kustomization.yaml      # 개발 환경 설정
    │   └── deployment-patch.yaml   # 개발 환경용 패치
    ├── staging/
    │   └── kustomization.yaml
    └── production/
        ├── kustomization.yaml      # 프로덕션 환경 설정
        └── deployment-patch.yaml   # 프로덕션 환경용 패치
```

## 사용 방법

### 1. 기본 배포 (모든 환경 동일)
```bash
# 기본 설정으로 배포
kubectl apply -k .
```

### 2. 개발 환경 배포
```bash
# 개발 환경으로 배포
kubectl apply -k overlays/development/

# 또는 네임스페이스 지정
NAMESPACE=development kubectl apply -k overlays/development/
```

### 3. 프로덕션 환경 배포
```bash
# 프로덕션 환경으로 배포
kubectl apply -k overlays/production/

# 또는 네임스페이스 지정
NAMESPACE=production kubectl apply -k overlays/production/
```

### 4. 환경별 삭제
```bash
# 개발 환경 삭제
kubectl delete -k overlays/development/

# 프로덕션 환경 삭제
kubectl delete -k overlays/production/
```

## 환경별 차이점

### 개발 환경 (overlays/development/)
- **네임스페이스**: development
- **레플리카**: 1개
- **리소스**: 최소 (128Mi 메모리, 100m CPU)
- **디버그 모드**: 활성화
- **로그 레벨**: debug
- **이미지 태그**: dev-latest

### 프로덕션 환경 (overlays/production/)
- **네임스페이스**: production
- **레플리카**: 3개
- **리소스**: 최대 (1Gi 메모리, 1000m CPU)
- **디버그 모드**: 비활성화
- **로그 레벨**: info
- **이미지 태그**: v1.0.0

## Kustomize의 장점

1. **DRY 원칙**: Don't Repeat Yourself - 공통 설정을 한 번만 정의
2. **환경별 관리**: 개발/스테이징/프로덕션 환경을 쉽게 관리
3. **버전 관리**: Git으로 환경별 설정을 버전 관리
4. **유지보수**: 기본 설정 변경 시 모든 환경에 자동 반영

## 실제 사용 예시

### 개발 환경 배포
```bash
# 1. 개발 환경 배포
kubectl apply -k overlays/development/

# 2. 배포 확인
kubectl get pods -n development -l app=ai-backend

# 3. 로그 확인
kubectl logs -n development -l app=ai-backend -f
```

### 프로덕션 환경 배포
```bash
# 1. 프로덕션 환경 배포
kubectl apply -k overlays/production/

# 2. 배포 확인
kubectl get pods -n production -l app=ai-backend

# 3. 서비스 확인
kubectl get svc -n production -l app=ai-backend
```

## 설정 변경 예시

### 개발 환경에서 레플리카 수 변경
`overlays/development/kustomization.yaml` 파일에서:
```yaml
replicas:
  - name: ai-backend-deployment
    count: 2  # 1에서 2로 변경
```

### 프로덕션 환경에서 이미지 태그 변경
`overlays/production/kustomization.yaml` 파일에서:
```yaml
images:
  - name: ai-backend
    newTag: v1.1.0  # v1.0.0에서 v1.1.0으로 변경
```

## 일반 kubectl vs Kustomize

### 일반 kubectl 사용
```bash
# 모든 파일을 개별적으로 배포
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
```

### Kustomize 사용 (권장)
```bash
# 하나의 명령으로 모든 리소스 배포
kubectl apply -k .

# 또는 환경별로
kubectl apply -k overlays/production/
```

## 결론

- **Kustomize**는 Kubernetes의 공식 도구
- 여러 환경을 효율적으로 관리할 수 있음
- 설정 중복을 줄이고 유지보수를 쉽게 만듦
- `kubectl apply -k .` 명령으로 간단하게 사용 가능
