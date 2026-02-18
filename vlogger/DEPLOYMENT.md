# 🚀 Railway 배포 가이드

## 📋 배포 전 준비사항

### 1. GitHub 저장소 확인
- **저장소 URL**: https://github.com/pynoodle/vlogger
- 모든 파일이 업로드되었는지 확인

### 2. OpenAI API 키 준비
- OpenAI 계정에서 API 키 생성
- API 키: OpenAI 계정에서 발급한 키를 환경 변수로 설정하세요

## 🚀 Railway 배포 단계

### 1단계: Railway 계정 생성
1. [Railway.app](https://railway.app) 접속
2. GitHub 계정으로 로그인
3. "Start a New Project" 클릭

### 2단계: 프로젝트 배포
1. "Deploy from GitHub repo" 선택
2. GitHub 저장소 `pynoodle/vlogger` 선택
3. "Deploy Now" 클릭

### 3단계: 환경 변수 설정
Railway 대시보드에서 다음 환경 변수를 설정:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4단계: 배포 완료
- Railway가 자동으로 빌드 및 배포를 진행
- 배포 완료 후 제공되는 URL로 접속 가능

## 🔧 배포 설정 파일

### Procfile
```
web: streamlit run english_persona_gui.py --server.port $PORT --server.address 0.0.0.0
```

### railway.toml
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run english_persona_gui.py --server.port $PORT --server.address 0.0.0.0"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### requirements.txt
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
openai>=1.0.0
google-api-python-client>=2.100.0
youtube-transcript-api>=0.6.1
yt-dlp>=2023.10.13
openai-whisper>=20231117
torch>=2.0.0
scikit-learn>=1.3.0
numpy>=1.24.0
requests>=2.31.0
```

## 🎯 배포 후 확인사항

### 1. 애플리케이션 접속
- Railway에서 제공하는 URL로 접속
- 로그인 테스트 (`.env`에 설정한 `AUTH_USER_ID` / `AUTH_USER_PW` 사용)

### 2. 기능 테스트
- 페르소나 선택 및 채팅
- 트렌드 분석 기능
- 관리자 대시보드 접속

### 3. 로그 확인
- Railway 대시보드에서 로그 확인
- 오류 발생 시 환경 변수 재확인

## 🛠️ 문제 해결

### 일반적인 문제
1. **빌드 실패**: requirements.txt 의존성 확인
2. **환경 변수 오류**: OPENAI_API_KEY 재설정
3. **포트 오류**: Procfile 및 railway.toml 확인

### 지원
- GitHub Issues: https://github.com/pynoodle/vlogger/issues
- Railway 문서: https://docs.railway.app

---

**Gen Z Influencer Persona Bot**