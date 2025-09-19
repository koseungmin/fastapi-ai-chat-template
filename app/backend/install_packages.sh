#!/bin/bash

echo "📦 패키지 설치 스크립트"
echo "======================"

# 1. 현재 디렉토리 확인
echo "1. 현재 디렉토리 확인..."
if [ ! -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml 파일을 찾을 수 없습니다."
    echo "올바른 프로젝트 디렉토리에서 실행해주세요."
    exit 1
fi
echo "✅ pyproject.toml 파일 확인 완료"

# 2. 가상환경 활성화 확인
echo -e "\n2. 가상환경 활성화 확인..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 가상환경이 활성화되어 있습니다: $VIRTUAL_ENV"
else
    echo "⚠️  가상환경이 활성화되어 있지 않습니다."
    echo "다음 명령어로 가상환경을 활성화해주세요:"
    echo "  source venv/bin/activate"
    echo "또는"
    echo "  conda activate your_env_name"
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 3. Python 버전 확인
echo -e "\n3. Python 버전 확인..."
python --version

# 4. pip 업그레이드
echo -e "\n4. pip 업그레이드..."
python -m pip install --upgrade pip
echo "✅ pip 업그레이드 완료"

# 5. 패키지 설치
echo -e "\n5. 패키지 설치..."
echo "pyproject.toml에서 의존성을 읽어서 설치합니다..."
pip install -e .
echo "✅ 패키지 설치 완료"

# 6. 설치된 패키지 확인
echo -e "\n6. 설치된 패키지 확인..."
echo "주요 패키지들:"
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|pydantic|redis|openai|pandas)"

# 7. 설치 완료 메시지
echo -e "\n🎉 패키지 설치 완료!"
echo "======================"
echo "다음 명령어로 서버를 실행하세요:"
echo "  python -m uvicorn ai_backend.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API 문서는 다음 URL에서 확인할 수 있습니다:"
echo "  http://localhost:8000/docs"
