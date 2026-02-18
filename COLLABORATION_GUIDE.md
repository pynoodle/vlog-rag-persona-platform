# 🤝 협업 가이드

## 📋 GitHub 협업 설정

### 1. 저장소 권한 설정
1. GitHub 저장소 → **Settings** → **Manage access**
2. **Invite a collaborator** 클릭
3. 협업자 GitHub 사용자명 또는 이메일 입력
4. 권한 레벨 선택:
   - **Read**: 코드 조회만 가능
   - **Write**: 코드 수정 및 푸시 가능
   - **Admin**: 모든 권한 (권한 관리 포함)

### 2. 협업자 초대
```bash
# 협업자에게 초대 링크 공유
https://github.com/pynoodle/vlogger/invitations
```

## 🚀 Railway 협업 설정

### 1. Railway 팀 초대
1. Railway 대시보드 → **Team** → **Invite Members**
2. 협업자 이메일 주소 입력
3. 권한 레벨 선택:
   - **Viewer**: 배포 상태 조회만 가능
   - **Developer**: 배포 및 환경 변수 수정 가능
   - **Admin**: 모든 권한

### 2. 환경 변수 공유
협업자에게 다음 환경 변수를 공유해야 합니다:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 🔧 개발 환경 설정

### 1. 로컬 개발 환경
```bash
# 저장소 클론
git clone https://github.com/pynoodle/vlogger.git
cd vlogger

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export OPENAI_API_KEY=your_api_key_here

# 애플리케이션 실행
streamlit run english_persona_gui.py
```

### 2. 개발 워크플로우
```bash
# 최신 코드 가져오기
git pull origin main

# 새 브랜치 생성
git checkout -b feature/new-feature

# 변경사항 커밋
git add .
git commit -m "Add new feature"

# 브랜치 푸시
git push origin feature/new-feature

# Pull Request 생성
# GitHub에서 "Compare & pull request" 클릭
```

## 📝 협업 규칙

### 1. 브랜치 전략
- **main**: 프로덕션 배포용
- **develop**: 개발 통합용
- **feature/**: 새로운 기능 개발용
- **hotfix/**: 긴급 수정용

### 2. 커밋 메시지 규칙
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가
chore: 빌드 설정 변경
```

### 3. Pull Request 규칙
- 제목: 명확한 변경사항 설명
- 설명: 변경 이유 및 영향도
- 리뷰어 지정
- 테스트 완료 확인

## 🔐 보안 고려사항

### 1. 민감한 정보 보호
- API 키는 환경 변수로만 관리
- `.env` 파일은 `.gitignore`에 추가
- `user_logs.json` 등 로그 파일은 공유하지 않음

### 2. 접근 권한 관리
- 최소 권한 원칙 적용
- 정기적인 권한 검토
- 불필요한 권한 제거

## 📞 연락처

### 문제 신고
- GitHub Issues: https://github.com/pynoodle/vlog-rag-persona-platform/issues

---

**Gen Z Influencer Persona Bot**
