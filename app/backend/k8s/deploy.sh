#!/bin/bash

# AI Backend Kubernetes Deployment Script
# 이 스크립트는 AI Backend 애플리케이션을 Kubernetes에 배포합니다.

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 스크립트 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

log_info "AI Backend Kubernetes Deployment Script 시작"
log_info "작업 디렉토리: $SCRIPT_DIR"

# kubectl 설치 확인
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl이 설치되지 않았습니다."
    exit 1
fi

# Kubernetes 클러스터 연결 확인
if ! kubectl cluster-info &> /dev/null; then
    log_error "Kubernetes 클러스터에 연결할 수 없습니다."
    exit 1
fi

log_success "Kubernetes 클러스터 연결 확인 완료"

# 네임스페이스 생성 (필요한 경우)
NAMESPACE=${NAMESPACE:-default}
if [ "$NAMESPACE" != "default" ]; then
    log_info "네임스페이스 '$NAMESPACE' 생성/확인 중..."
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
fi

# 배포 순서 정의
RESOURCES=(
    "configmap.yaml"
    "secret.yaml"
    "persistent-volume.yaml"
    "deployment.yaml"
    "service.yaml"
    "ingress.yaml"
)

# 각 리소스 배포
for resource in "${RESOURCES[@]}"; do
    if [ -f "$resource" ]; then
        log_info "$resource 배포 중..."
        
        # 네임스페이스가 default가 아닌 경우 네임스페이스 오버라이드
        if [ "$NAMESPACE" != "default" ]; then
            kubectl apply -f "$resource" -n "$NAMESPACE"
        else
            kubectl apply -f "$resource"
        fi
        
        if [ $? -eq 0 ]; then
            log_success "$resource 배포 완료"
        else
            log_error "$resource 배포 실패"
            exit 1
        fi
    else
        log_warning "$resource 파일을 찾을 수 없습니다."
    fi
done

# 배포 상태 확인
log_info "배포 상태 확인 중..."

# Pod 상태 확인
log_info "Pod 상태 확인:"
kubectl get pods -l app=ai-backend -n "$NAMESPACE" -o wide

# 서비스 상태 확인
log_info "서비스 상태 확인:"
kubectl get services -l app=ai-backend -n "$NAMESPACE"

# Ingress 상태 확인
log_info "Ingress 상태 확인:"
kubectl get ingress -l app=ai-backend -n "$NAMESPACE"

# Pod가 준비될 때까지 대기
log_info "Pod가 준비될 때까지 대기 중..."
kubectl wait --for=condition=ready pod -l app=ai-backend -n "$NAMESPACE" --timeout=300s

if [ $? -eq 0 ]; then
    log_success "모든 Pod가 준비되었습니다."
else
    log_warning "일부 Pod가 준비되지 않았습니다. 수동으로 확인해주세요."
fi

# 헬스 체크
log_info "헬스 체크 수행 중..."

# Pod 이름 가져오기
POD_NAME=$(kubectl get pods -l app=ai-backend -n "$NAMESPACE" -o jsonpath='{.items[0].metadata.name}')

if [ -n "$POD_NAME" ]; then
    log_info "Pod '$POD_NAME'에서 헬스 체크 수행..."
    
    # Pod 내부에서 헬스 체크
    if kubectl exec "$POD_NAME" -n "$NAMESPACE" -- curl -f http://localhost:8000/health &> /dev/null; then
        log_success "헬스 체크 성공"
    else
        log_warning "헬스 체크 실패 - 애플리케이션이 아직 준비되지 않았을 수 있습니다."
    fi
else
    log_warning "Pod를 찾을 수 없습니다."
fi

# 배포 완료 메시지
echo ""
log_success "AI Backend Kubernetes 배포가 완료되었습니다!"
echo ""
log_info "다음 명령어로 애플리케이션에 접근할 수 있습니다:"
echo "  kubectl port-forward svc/ai-backend-service 8000:8000 -n $NAMESPACE"
echo "  curl http://localhost:8000/health"
echo ""
log_info "로그 확인:"
echo "  kubectl logs -l app=ai-backend -n $NAMESPACE -f"
echo ""
log_info "Pod 상태 확인:"
echo "  kubectl get pods -l app=ai-backend -n $NAMESPACE"
echo ""

# 환경별 추가 정보
if [ "$NAMESPACE" = "production" ]; then
    log_info "프로덕션 환경 배포 완료"
    log_warning "다음을 확인해주세요:"
    echo "  - Ingress 설정이 올바른지 확인"
    echo "  - SSL 인증서 설정 확인"
    echo "  - 모니터링 설정 확인"
    echo "  - 백업 설정 확인"
elif [ "$NAMESPACE" = "staging" ]; then
    log_info "스테이징 환경 배포 완료"
    log_info "테스트 후 프로덕션 배포를 진행하세요."
else
    log_info "개발 환경 배포 완료"
fi

log_success "배포 스크립트 실행 완료"
