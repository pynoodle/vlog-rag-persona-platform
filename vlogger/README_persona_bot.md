# 🎭 Gen Z 인플루언서 페르소나봇

Gen Z 인플루언서들의 라이프스타일을 분석하여 만든 AI 페르소나 챗봇 시스템입니다.

## 🌟 주요 기능

### 💬 대화 기능
- **5개의 페르소나**: Emma, Victoria, Misha, Philip, James
- **실시간 대화**: 스트리밍 방식의 자연스러운 대화
- **개성 있는 응답**: 각 페르소나의 고유한 성격과 말투
- **빠른 질문**: 페르소나별 맞춤형 빠른 질문 버튼

### 📈 트렌드 분석
- **페르소나별 특화 트렌드**: 각 전문분야에 맞는 트렌드 분석
- **키워드 시각화**: 상위 키워드 차트로 트렌드 파악
- **카테고리별 분석**: 세부 카테고리별 트렌드 인사이트

### 🏠 라이프스타일 가이드
- **전문분야별 가이드**: 각 페르소나의 전문분야에 맞는 실용적 팁
- **라이프스타일 통계**: 키워드 분포로 라이프스타일 패턴 분석
- **맞춤형 조언**: 개인화된 라이프스타일 가이드 제공

### 🎬 콘텐츠 제작
- **콘텐츠 아이디어 생성**: 인플루언서 스타일의 콘텐츠 아이디어
- **유형별 콘텐츠**: 페르소나별 특화된 콘텐츠 유형 제안
- **제작 통계**: 콘텐츠 키워드 분포 시각화

## 👥 페르소나 소개

### 👩‍🍳 Emma (클러스터 0)
- **나이**: 22세
- **전문분야**: 요리, 패션, 예술, 뷰티, 여행
- **특징**: 다재다능한 라이프스타일 인플루언서
- **대표 문구**: "OMG, this is so cute!"
- **지식베이스**: 20개 전사본

### 🏠 Victoria (클러스터 1)
- **나이**: 24세
- **전문분야**: 홈 데코, 일상 공유, 반려동물 케어
- **특징**: 홈 & 뷰티 중심 라이프스타일 인플루언서
- **대표 문구**: "Let me show you my cozy life!"
- **지식베이스**: 351개 전사본 (가장 풍부)

### 📚 Misha (클러스터 2)
- **나이**: 23세
- **전문분야**: 독서, 저널링, 자기계발, 테크
- **특징**: 활발한 콘텐츠 크리에이터
- **대표 문구**: "Let's make today amazing!"
- **지식베이스**: 105개 전사본

### 📸 Philip (클러스터 3)
- **나이**: 25세
- **전문분야**: 사진, 예술, 크래프트, 요리
- **특징**: 예술 & 크래프트 전문가
- **대표 문구**: "Art is everywhere"
- **지식베이스**: 50개 전사본

### 💄 James (클러스터 4)
- **나이**: 26세
- **전문분야**: 뷰티, 패션, 스타일링
- **특징**: 뷰티 & 패션 전문가
- **대표 문구**: "Beauty is power"
- **지식베이스**: 10개 전사본

## 🚀 사용 방법

### 1. 기본 실행
```bash
# 기본 GUI 실행
streamlit run persona_gui.py

# 개선된 GUI 실행
streamlit run enhanced_persona_gui.py
```

### 2. 프로그래밍 방식 사용
```python
from cluster_chatbots import ChatbotManager

# 챗봇 매니저 생성
manager = ChatbotManager()

# 특정 페르소나 선택
chatbot = manager.select_chatbot(0)  # Emma 선택

# 대화
response = chatbot.chat("안녕! 오늘 뭐 해?")
print(response)

# 트렌드 분석
trend_analysis = chatbot.get_trend_analysis("뷰티")
print(trend_analysis)

# 라이프스타일 팁
lifestyle_tips = chatbot.get_lifestyle_tips()
print(lifestyle_tips)
```

### 3. 데모 실행
```bash
# 자동 데모
python demo_chatbot.py

# 대화형 데모
python chatbot_interface.py
```

## 🛠️ 기술 스택

### 백엔드
- **Python 3.8+**
- **OpenAI GPT-4o-mini**: AI 응답 생성
- **scikit-learn**: 클러스터링 및 데이터 분석
- **pandas**: 데이터 처리
- **plotly**: 시각화

### 프론트엔드
- **Streamlit**: 웹 GUI 프레임워크
- **CSS**: 커스텀 스타일링
- **HTML**: 동적 콘텐츠

### 데이터
- **RAG (Retrieval-Augmented Generation)**: STT 데이터 기반 지식베이스
- **K-means 클러스터링**: 페르소나 분류
- **키워드 분석**: 라이프스타일 패턴 추출

## 📊 데이터 분석 결과

### 클러스터별 분포
- **클러스터 0 (Emma)**: 1개 채널, 20개 전사본
- **클러스터 1 (Victoria)**: 22개 채널, 351개 전사본
- **클러스터 2 (Misha)**: 3개 채널, 105개 전사본
- **클러스터 3 (Philip)**: 1개 채널, 50개 전사본
- **클러스터 4 (James)**: 1개 채널, 10개 전사본

### 주요 라이프스타일 액티비티
1. **요리 & 식사**: 82.9% (257개 영상)
2. **독서 & 저널링**: 66.5% (206개 영상)
3. **쇼핑 & 하울**: 62.6% (194개 영상)
4. **마인드풀니스 & 휴식**: 59.4% (184개 영상)
5. **운동 & 피트니스**: 55.2% (171개 영상)

## 🔧 설정 방법

### 1. 환경 변수 설정
```bash
# Windows
set OPENAI_API_KEY=your-api-key-here

# Mac/Linux
export OPENAI_API_KEY=your-api-key-here
```

### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 데이터 준비
- `channel_stats.csv`: 채널 통계 데이터
- `youtube_data/`: STT 전사본 데이터
- `persona_clusters.csv`: 클러스터링 결과

## 📁 프로젝트 구조

```
vlogger/
├── persona_gui.py              # 기본 GUI
├── enhanced_persona_gui.py     # 개선된 GUI
├── cluster_chatbots.py         # 챗봇 클래스들
├── persona_chatbot_rag.py      # RAG 기반 챗봇
├── demo_chatbot.py             # 데모 스크립트
├── chatbot_interface.py        # 대화형 인터페이스
├── persona_clustering.py       # 클러스터링 스크립트
├── analyze_clusters.py         # 클러스터 분석
└── README_persona_bot.md       # 사용법 가이드
```

## 🎯 활용 방안

### 1. 트렌드 분석
- 각 페르소나별로 특화된 트렌드 인사이트 제공
- 키워드 분석을 통한 트렌드 패턴 파악
- 카테고리별 세부 트렌드 분석

### 2. 개인화된 조언
- 사용자의 관심사에 맞는 맞춤형 라이프스타일 가이드
- 페르소나별 전문분야에 특화된 실용적 팁
- 개인화된 콘텐츠 아이디어 생성

### 3. 콘텐츠 제작
- 인플루언서 스타일의 콘텐츠 아이디어 생성
- 페르소나별 특화된 콘텐츠 유형 제안
- 트렌드 기반 콘텐츠 전략 수립

### 4. 마케팅 인사이트
- Gen Z 라이프스타일 패턴 분석
- 타겟별 맞춤형 마케팅 전략
- 인플루언서 마케팅 인사이트

## 🔮 향후 개선 계획

### 1. 데이터 확장
- 더 많은 채널과 영상 데이터 수집
- James 클러스터의 데이터 부족 문제 해결
- 실시간 데이터 업데이트 기능

### 2. 기능 개선
- 음성 대화 기능 추가
- 이미지 생성 기능 통합
- 다국어 지원

### 3. 사용자 경험
- 모바일 최적화
- 개인화 설정 기능
- 대화 기록 관리 기능

## 📞 문의사항

프로젝트에 대한 문의사항이나 개선 제안이 있으시면 언제든지 연락주세요!

---

**🎭 Gen Z 인플루언서 페르소나봇으로 더 나은 라이프스타일을 경험해보세요!**
