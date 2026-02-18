# 🎭 Gen Z Influencer Persona Bot

> **Built:** October 2025

YouTube 데이터를 수집하고 AI 클러스터링을 통해 Gen Z 인플루언서들의 라이프스타일을 분석하여 개인화된 페르소나 봇을 제공합니다.

## 🚀 주요 기능

### 🔐 로그인 시스템
- 로그인 정보는 `.env` 파일의 `AUTH_USER_ID`, `AUTH_USER_PW`, `AUTH_ADMIN_ID`, `AUTH_ADMIN_PW` 환경 변수로 설정하세요.

### 🎭 페르소나 봇
- **Emma** 👩‍🍳: 다재다능한 라이프스타일 (요리, 패션, 예술, 뷰티, 여행)
- **Victoria** 🏠: 홈 & 뷰티 라이프스타일 (홈데코, 일상, 반려동물 케어)
- **Misha** 📚: 활발한 콘텐츠 크리에이터 (독서, 저널링, 자기계발, 테크)
- **Philip** 📸: 예술 & 공예 전문가 (사진, 예술, 공예, 요리)
- **James** 💄: 뷰티 & 패션 전문가 (뷰티, 패션, 스타일링)

### 💬 멀티 채팅
- 여러 페르소나와 동시 대화
- 각 페르소나의 고유한 성격과 말투로 응답
- RAG 기반 지식 베이스 활용

### 📊 분석 기능
- **📈 트렌드 분석**: 페르소나별 트렌드 인사이트
- **🏠 라이프스타일 가이드**: 전문 분야별 실용적 팁
- **🎬 콘텐츠 제작**: 인플루언서 스타일 콘텐츠 아이디어

### 👨‍💼 관리자 대시보드
- 사용자 활동 로그 모니터링
- IP별 접속 통계
- 검색 및 사용 패턴 분석

## 🛠️ 기술 스택

### AI/ML
- **OpenAI GPT-4o-mini**: 대화 생성
- **Whisper STT**: 음성을 텍스트로 변환
- **K-means Clustering**: 유사한 라이프스타일 그룹화
- **PCA**: 차원 축소 및 시각화

### 웹 기술
- **Streamlit**: 웹 애플리케이션 프레임워크
- **Python**: 백엔드 개발
- **JSON**: 데이터 처리
- **실시간 채팅**: 스트리밍 응답

### 데이터 분석
- **Pandas**: 데이터 조작
- **NumPy**: 수치 계산
- **Scikit-learn**: 머신러닝
- **Plotly**: 데이터 시각화

## 📊 데이터 수집 과정

1. **YouTube API v3**를 사용하여 Gen Z 인플루언서 채널 데이터 수집
2. **STT (Speech-to-Text)** 기술로 비디오 음성을 텍스트로 변환
3. **Whisper AI** 모델을 사용한 고품질 한국어 전사
4. **K-means 클러스터링**으로 유사한 라이프스타일 그룹화
5. **PCA (주성분 분석)**로 차원 축소 및 시각화

## 🚀 배포 방법

### Railway 배포
1. GitHub 저장소를 Railway에 연결
2. 환경 변수 설정:
   - `OPENAI_API_KEY`: OpenAI API 키
3. 자동 배포 완료

### 로컬 실행
```bash
pip install -r requirements.txt
streamlit run english_persona_gui.py
```

## 🔍 RAG Architecture

YouTube 영상 트랜스크립트를 기반으로 각 페르소나의 지식 베이스를 구성하고, 질의응답 시 관련 콘텐츠를 검색해 응답을 생성합니다.

```
1. Whisper STT          → YouTube 영상 음성을 텍스트로 전사
2. Paragraph Chunking   → 문단 단위 분리 (최소 50자 필터링)
3. TF-IDF Vectorization → 1-2 gram, max 1,000 features로 인덱싱
4. Cosine Similarity    → 질의와 청크 간 유사도 계산
5. Top-k Retrieval      → 상위 k=2~3개 청크 선택
6. Prompt Assembly      → 시스템 프롬프트 + 페르소나 정보 + 검색 컨텍스트 결합
7. LLM Response         → GPT-4o-mini로 페르소나 스타일 응답 생성
```

> **Note:** 현 구현은 TF-IDF 기반 in-memory 검색을 사용합니다. 대규모 확장 시 FAISS 또는 ChromaDB로 전환 가능한 구조입니다.

## 🛡️ Grounding Strategy

실제로 구현된 hallucination 완화 장치:

| 항목 | 구현 내용 |
|------|-----------|
| **Similarity Threshold** | 코사인 유사도 < 0.1인 청크는 컨텍스트에서 제외 (`simple_rag_manager.py:166`) |
| **Source Citation** | 검색된 청크에 페르소나 이름·역할을 태깅해 응답에 출처 표시 |
| **Graceful Fallback** | 유사도 임계값을 초과하는 청크가 없을 경우 빈 컨텍스트로 안전하게 처리 |
| **Retrieval-grounded Prompting** | 검색된 실제 트랜스크립트 내용을 프롬프트에 주입해 창작 응답 억제 |

## 📐 Evaluation

| 항목 | 내용 |
|------|------|
| **Retrieval Quality** | TF-IDF 코사인 유사도 점수로 검색 적합도 측정 |
| **Persona Coherence** | 페르소나별 도메인 키워드 매칭률로 캐릭터 일관성 정성 평가 |
| **Future Improvements** | Precision@k 측정, 사용자 피드백 루프, semantic embedding(OpenAI/SBERT) 전환 검토 |

## 📁 프로젝트 구조

```
vlogger/
├── english_persona_gui.py      # 메인 Streamlit 애플리케이션
├── persona_chatbot_rag.py      # RAG 기반 페르소나 챗봇
├── cluster_chatbots.py         # 클러스터별 챗봇 관리
├── persona_clusters.csv        # 클러스터링 결과
├── channel_stats.csv           # 채널 통계
├── user_logs.json             # 사용자 로그
├── requirements.txt           # Python 의존성
├── Procfile                   # Railway 배포 설정
├── railway.toml              # Railway 설정
└── README.md                  # 프로젝트 설명
```

## 🔧 환경 변수

- `OPENAI_API_KEY`: OpenAI API 키 (필수)

## 📈 프로젝트 통계

- **총 채널 수**: 30개 Gen Z 인플루언서 채널
- **총 영상 수**: 1,560개 영상
- **STT 파일 수**: 1,560개 전사본
- **총 조회수**: 500M+ 조회수

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

## 📞 연락처

- **프로젝트 링크**: [https://github.com/pynoodle/vlog-rag-persona-platform](https://github.com/pynoodle/vlog-rag-persona-platform)

---

**Gen Z Influencer Persona Bot**