# 🤝 기여 가이드

## 📋 기여하기 전에

### 1. 저장소 포크
1. GitHub에서 저장소를 포크합니다
2. 로컬에 클론합니다:
```bash
git clone https://github.com/YOUR_USERNAME/vlogger.git
cd vlogger
```

### 2. 개발 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export OPENAI_API_KEY=your_api_key_here

# 애플리케이션 실행
streamlit run english_persona_gui.py
```

## 🔄 개발 워크플로우

### 1. 브랜치 생성
```bash
# 최신 코드 가져오기
git checkout main
git pull origin main

# 새 브랜치 생성
git checkout -b feature/your-feature-name
```

### 2. 개발 및 테스트
- 코드 변경사항 작성
- 로컬에서 테스트
- 코드 스타일 확인

### 3. 커밋 및 푸시
```bash
# 변경사항 추가
git add .

# 커밋 (명확한 메시지 작성)
git commit -m "feat: add new feature"

# 브랜치 푸시
git push origin feature/your-feature-name
```

### 4. Pull Request 생성
1. GitHub에서 "Compare & pull request" 클릭
2. 제목과 설명 작성
3. 리뷰어 지정
4. PR 생성

## 📝 코딩 규칙

### 1. Python 스타일
- PEP 8 스타일 가이드 준수
- 함수명은 snake_case
- 클래스명은 PascalCase
- 상수는 UPPER_CASE

### 2. 커밋 메시지
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가
chore: 빌드 설정 변경
```

### 3. 주석 작성
- 복잡한 로직에는 주석 추가
- 함수/클래스에는 docstring 작성
- TODO 주석은 이슈로 등록

## 🧪 테스트

### 1. 로컬 테스트
```bash
# 애플리케이션 실행
streamlit run english_persona_gui.py

# 모든 기능 테스트
# - 로그인/로그아웃
# - 페르소나 선택
# - 채팅 기능
# - 관리자 대시보드
```

### 2. 테스트 체크리스트
- [ ] 로그인 시스템 작동
- [ ] 페르소나 선택 및 채팅
- [ ] 트렌드 분석 기능
- [ ] 관리자 대시보드
- [ ] 로그 백업/복원

## 🐛 버그 신고

### 1. 이슈 생성
1. GitHub Issues에서 "New issue" 클릭
2. 버그 템플릿 선택
3. 상세한 정보 입력

### 2. 포함할 정보
- 버그 설명
- 재현 단계
- 예상 동작
- 실제 동작
- 환경 정보
- 스크린샷 (해당하는 경우)

## 🚀 기능 요청

### 1. 이슈 생성
1. GitHub Issues에서 "New issue" 클릭
2. 기능 요청 템플릿 선택
3. 상세한 정보 입력

### 2. 포함할 정보
- 기능 설명
- 사용 사례
- 예상 동작
- 목업/스크린샷 (해당하는 경우)

## 📞 연락처

### 문제 신고
- GitHub Issues: https://github.com/pynoodle/vlog-rag-persona-platform/issues

---

**Gen Z Influencer Persona Bot**
