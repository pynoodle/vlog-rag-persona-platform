#!/bin/bash

# Railway 배포를 위한 시작 스크립트
export PYTHONPATH="${PYTHONPATH}:."

# Streamlit 설정
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# OpenAI API 키 확인
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY not set. Some features may not work."
fi

# Streamlit 실행
exec streamlit run english_persona_gui.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false
