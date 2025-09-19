#!/bin/bash

# AI Backend Kubernetes Undeployment Script
# 이 스크립트는 AI Backend 애플리케이션을 Kubernetes에서 제거합니다.

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

log_info "AI Backend Kubernetes Undeployment Script 시작"
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

# 네임스페이스 확인
NAMESPACE=${NAMESPACE:-default}
log_info "네임스페이스: $NAMESPACE"

# 삭제 확인
if [ "$1" != "--force" ]; then
    echo ""
    log_warning "이 작업은 다음 리소스들을 삭제합니다:"
    echo "  - Deployment: ai-backend-deployment"
    echo "  - Service: ai-backend-service, ai-backend-nodeport"
    echo "  - Ingress: ai-backend-ingress, ai-backend-ingress-simple"
    echo "  - ConfigMap: ai-backend-config"
    echo "  - Secret: ai-backend-secret"
    echo "  - PVC: ai-backend-pvc (데이터 보존됨)"
    echo "  - PV: ai-backend-pv (데이터 보존됨)"
    echo ""
    
    read -p "계속하시겠습니까? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "작업이 취소되었습니다."
        exit 0
    fi
fi

# 삭제 순서 정의 (의존성 고려)
RESOURCES=(
    "ingress.yaml"
    "service.yaml"
    "deployment.yaml"
    "configmap.yaml"
    "secret.yaml"
    "persistent-volume.yaml"
)

# 각 리소스 삭제
for resource in "${RESOURCES[@]}"; do
    if [ -f "$resource" ]; then
        log_info "$resource 삭제 중..."
        
        # 네임스페이스가 default가 아닌 경우 네임스페이스 오버라이드
        if [ "$NAMESPACE" != "default" ]; then
            kubectl delete -f "$resource" -n "$NAMESPACE" --ignore-not-found=true
        else
            kubectl delete -f "$resource" --ignore-not-found=true
        fi
        
        if [ $? -eq 0 ]; then
            log_success "$resource 삭제 완료"
        else
            log_warning "$resource 삭제 중 오류 발생 (무시됨)"
        fi
    else
        log_warning "$resource 파일을 찾을 수 없습니다."
    fi
done

# 리소스 정리 확인
log_info "리소스 정리 상태 확인 중..."

# 남은 리소스 확인
log_info "남은 Pod 확인:"
kubectl get pods -l app=ai-backend -n "$NAMESPACE" --ignore-not-found=true

log_info "남은 서비스 확인:"
kubectl get services -l app=ai-backend -n "$NAMESPACE" --ignore-not-found=true

log_info "남은 Ingress 확인:"
kubectl get ingress -l app=ai-backend -n "$NAMESPACE" --ignore-not-found=true

# PersistentVolume과 PersistentVolumeClaim은 데이터 보존을 위해 기본적으로 삭제하지 않음
log_info "PersistentVolume 상태 확인:"
kubectl get pv ai-backend-pv --ignore-not-found=true

log_info "PersistentVolumeClaim 상태 확인:"
kubectl get pvc ai-backend-pvc -n "$NAMESPACE" --ignore-not-found=true

# 완전 삭제 옵션
if [ "$1" = "--force" ] || [ "$2" = "--delete-pv" ]; then
    log_warning "완전 삭제 모드: PersistentVolume과 PersistentVolumeClaim도 삭제합니다."
    
    log_info "PersistentVolumeClaim 삭제 중..."
    kubectl delete pvc ai-backend-pvc -n "$NAMESPACE" --ignore-not-found=true
    
    log_info "PersistentVolume 삭제 중..."
    kubectl delete pv ai-backend-pv --ignore-not-found=true
    
    log_warning "데이터가 영구적으로 삭제되었습니다!"
fi

# 네임스페이스 삭제 (선택사항)
if [ "$1" = "--force" ] && [ "$NAMESPACE" != "default" ]; then
    log_info "네임스페이스 '$NAMESPACE' 삭제 중..."
    kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
    log_success "네임스페이스 삭제 완료"
fi

# 정리 완료 메시지
echo ""
log_success "AI Backend Kubernetes 정리가 완료되었습니다!"
echo ""

if [ "$1" != "--delete-pv" ] && [ "$2" != "--delete-pv" ]; then
    log_info "데이터 보존 안내:"
    echo "  - PersistentVolume과 PersistentVolumeClaim은 데이터 보존을 위해 유지됩니다."
    echo "  - 완전 삭제를 원한다면 다음 명령어를 사용하세요:"
    echo "    ./undeploy.sh --force --delete-pv"
    echo ""
fi

log_info "정리된 리소스:"
echo "  ✓ Deployment: ai-backend-deployment"
echo "  ✓ Service: ai-backend-service, ai-backend-nodeport"
echo "  ✓ Ingress: ai-backend-ingress, ai-backend-ingress-simple"
echo "  ✓ ConfigMap: ai-backend-config"
echo "  ✓ Secret: ai-backend-secret"

if [ "$1" = "--delete-pv" ] || [ "$2" = "--delete-pv" ]; then
    echo "  ✓ PVC: ai-backend-pvc (데이터 삭제됨)"
    echo "  ✓ PV: ai-backend-pv (데이터 삭제됨)"
else
    echo "  ⚠ PVC: ai-backend-pvc (데이터 보존됨)"
    echo "  ⚠ PV: ai-backend-pv (데이터 보존됨)"
fi

if [ "$1" = "--force" ] && [ "$NAMESPACE" != "default" ]; then
    echo "  ✓ Namespace: $NAMESPACE"
fi

echo ""
log_success "정리 스크립트 실행 완료"
