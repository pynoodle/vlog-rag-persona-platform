# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
import sys
from datetime import datetime
from cluster_chatbots import ChatbotManager
import hashlib
import ipaddress
import requests

# 인코딩 설정 (Windows 환경에서 한글 표시를 위한 환경 변수 설정)
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class EnglishPersonaGUI:
    def __init__(self):
        self.manager = ChatbotManager()
        
        # 페르소나 정보
        self.personas = {
            0: {
                'name': 'Emma',
                'avatar': '👩‍🍳',
                'age': '22세',
                'personality': ['창의적', '다재다능', '트렌드 민감', '에너지틱', '감성적'],
                'interests': ['요리', '패션', '예술', '뷰티', '여행'],
                'speech_style': '친근하고 편안한 말투, 이모지 자주 사용',
                'description': '다재다능한 라이프스타일',
                'specialty': '요리, 패션, 예술, 뷰티, 여행',
                'catchphrase': '와, 이거 너무 귀여워!'
            },
            1: {
                'name': 'Victoria',
                'avatar': '🏠',
                'age': '24세',
                'personality': ['실용적', '감성적', '홈 데코 전문', '일상 공유', '친근함'],
                'interests': ['홈 데코', '요리', '일상 공유', '반려동물', '테크'],
                'speech_style': '따뜻하고 편안한 말투, 일상적인 표현',
                'description': '홈 & 뷰티 라이프스타일',
                'specialty': '홈데코, 일상, 반려동물 케어',
                'catchphrase': '내 아늑한 일상을 보여줄게'
            },
            2: {
                'name': 'Misha',
                'avatar': '📚',
                'age': '23세',
                'personality': ['에너지틱', '창의적', '자기계발', '활동적', '다양함'],
                'interests': ['독서', '저널링', '테크', '요리', '홈 데코'],
                'speech_style': '활발하고 긍정적인 말투, 자기계발 관련 표현',
                'description': '활발한 콘텐츠 크리에이터',
                'specialty': '독서, 저널링, 자기계발, 테크',
                'catchphrase': '오늘을 멋지게 만들어보자!'
            },
            3: {
                'name': 'Philip',
                'avatar': '📸',
                'age': '25세',
                'personality': ['예술적', '창의적', '디테일 지향', '독창적', '감성적'],
                'interests': ['사진', '예술', '요리', '테크', '크래프트'],
                'speech_style': '예술적이고 세련된 말투, 창의적 표현',
                'description': '예술 & 공예 전문가',
                'specialty': '사진, 예술, 공예, 요리',
                'catchphrase': '예술은 어디에나 있어'
            },
            4: {
                'name': 'James',
                'avatar': '💄',
                'age': '26세',
                'personality': ['전문적', '트렌드 민감', '스타일리시', '뷰티 전문', '패션 전문'],
                'interests': ['뷰티', '패션', '요리', '예술', '테크'],
                'speech_style': '전문적이고 세련된 말투, 뷰티/패션 전문 용어',
                'description': '뷰티 & 패션 전문가',
                'specialty': '뷰티, 패션, 스타일링',
                'catchphrase': '뷰티는 힘이야'
            }
        }
        
        # 사용자 데이터베이스 파일
        self.db_file = "user_logs.json"
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "users": {},
                    "admin_logs": [],
                    "search_logs": [],
                    "usage_logs": []
                }, f, ensure_ascii=False, indent=2)
    
    def get_client_ip(self):
        """클라이언트 IP 주소 가져오기"""
        try:
            # Streamlit에서 제공하는 세션 정보에서 IP 가져오기
            if hasattr(st.session_state, 'client_ip'):
                return st.session_state.client_ip
            
            # 외부 서비스에서 IP 가져오기
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            if response.status_code == 200:
                ip = response.json().get('ip', 'unknown')
                st.session_state.client_ip = ip
                return ip
        except:
            pass
        return 'unknown'
    
    def log_user_activity(self, user_id, activity_type, details=""):
        """사용자 활동 로그 기록"""
        try:
            # 기존 데이터 로드 (파일이 없으면 새로 생성)
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    "users": {},
                    "admin_logs": [],
                    "search_logs": [],
                    "usage_logs": []
                }
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "ip": self.get_client_ip(),
                "activity": activity_type,
                "details": details
            }
            
            if activity_type == "search":
                data["search_logs"].append(log_entry)
            elif activity_type == "usage":
                data["usage_logs"].append(log_entry)
            elif activity_type == "admin":
                data["admin_logs"].append(log_entry)
            
            # 로그 파일 저장
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            # 백업 파일도 생성 (데이터 손실 방지)
            backup_file = f"user_logs_backup_{datetime.now().strftime('%Y%m%d')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            st.error(f"로그 기록 중 오류: {e}")
    
    def authenticate_user(self, username, password):
        """사용자 인증"""
        # 일반 사용자 인증
        import os
        auth_user_id = os.getenv("AUTH_USER_ID")
        auth_user_pw = os.getenv("AUTH_USER_PW")
        auth_admin_id = os.getenv("AUTH_ADMIN_ID")
        auth_admin_pw = os.getenv("AUTH_ADMIN_PW")
        if not all([auth_user_id, auth_user_pw, auth_admin_id, auth_admin_pw]):
            return False
        if username == auth_user_id and password == auth_user_pw:
            return "user"
        # 관리자 인증
        elif username == auth_admin_id and password == auth_admin_pw:
            return "admin"
        return False
    
    def show_login_page(self):
        """로그인 페이지 표시"""
        st.title("🔐 Gen Z 인플루언서 페르소나 봇 로그인")
        
        with st.container():
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 2rem;'>
                <p style='font-size: 0.8rem; margin-bottom: 0.5rem; opacity: 0.8;'>Gen Z Influencer Persona Bot</p>
                <h1>🎭 Gen Z Influencer Persona Bot</h1>
                <p>로그인하여 페르소나 봇과 대화하세요!</p>
            </div>
            """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### 로그인 정보")
            username = st.text_input("사용자 ID:", placeholder="사용자 ID를 입력하세요")
            password = st.text_input("비밀번호:", type="password", placeholder="비밀번호를 입력하세요")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.form_submit_button("🔑 로그인", use_container_width=True)
            with col2:
                admin_button = st.form_submit_button("👨‍💼 관리자 로그인", use_container_width=True)
            
            if login_button:
                if username and password:
                    auth_result = self.authenticate_user(username, password)
                    if auth_result == "user":
                        st.session_state.authenticated = True
                        st.session_state.user_type = "user"
                        st.session_state.username = username
                        self.log_user_activity(username, "login", "일반 사용자 로그인")
                        st.success("로그인 성공! 페르소나 봇을 사용할 수 있습니다.")
                        st.rerun()
                    elif auth_result == "admin":
                        st.session_state.authenticated = True
                        st.session_state.user_type = "admin"
                        st.session_state.username = username
                        self.log_user_activity(username, "admin", "관리자 로그인")
                        st.success("관리자 로그인 성공!")
                        st.rerun()
                    else:
                        st.error("잘못된 사용자 ID 또는 비밀번호입니다.")
                else:
                    st.warning("사용자 ID와 비밀번호를 입력해주세요.")
            
            if admin_button:
                if username and password:
                    auth_result = self.authenticate_user(username, password)
                    if auth_result == "admin":
                        st.session_state.authenticated = True
                        st.session_state.user_type = "admin"
                        st.session_state.username = username
                        self.log_user_activity(username, "admin", "관리자 로그인")
                        st.success("관리자 로그인 성공!")
                        st.rerun()
                    else:
                        st.error("관리자 인증에 실패했습니다.")
                else:
                    st.warning("관리자 ID와 비밀번호를 입력해주세요.")
    
    def show_admin_dashboard(self):
        """관리자 대시보드 표시"""
        st.title("👨‍💼 관리자 대시보드")
        
        # 사이드바에 로그아웃 버튼
        with st.sidebar:
            if st.button("🚪 로그아웃", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_type = None
                st.session_state.username = None
                st.rerun()
        
        # 로그 데이터 로드
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            st.error("로그 데이터를 불러올 수 없습니다.")
            return
        
        # 탭 생성
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 전체 통계", "🔍 검색 로그", "👥 사용 로그", "🔐 관리자 로그", "💾 로그 관리"])
        
        with tab1:
            st.markdown("### 📊 전체 통계")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("총 검색 수", len(data.get("search_logs", [])))
            with col2:
                st.metric("총 사용 수", len(data.get("usage_logs", [])))
            with col3:
                st.metric("관리자 접속 수", len(data.get("admin_logs", [])))
            with col4:
                unique_ips = set()
                for log in data.get("search_logs", []) + data.get("usage_logs", []):
                    unique_ips.add(log.get("ip", "unknown"))
                st.metric("고유 IP 수", len(unique_ips))
        
        with tab2:
            st.markdown("### 🔍 검색 로그")
            search_logs = data.get("search_logs", [])
            if search_logs:
                # IP별 검색 통계
                ip_search_count = {}
                for log in search_logs:
                    ip = log.get("ip", "unknown")
                    ip_search_count[ip] = ip_search_count.get(ip, 0) + 1
                
                st.markdown("#### IP별 검색 통계")
                for ip, count in sorted(ip_search_count.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"**{ip}**: {count}회")
                
                st.markdown("#### 최근 검색 로그")
                for log in search_logs[-10:]:  # 최근 10개
                    st.write(f"**{log.get('timestamp', 'N/A')}** - IP: {log.get('ip', 'unknown')} - {log.get('details', 'N/A')}")
            else:
                st.info("검색 로그가 없습니다.")
        
        with tab3:
            st.markdown("### 👥 사용 로그")
            usage_logs = data.get("usage_logs", [])
            if usage_logs:
                # IP별 사용 통계
                ip_usage_count = {}
                for log in usage_logs:
                    ip = log.get("ip", "unknown")
                    ip_usage_count[ip] = ip_usage_count.get(ip, 0) + 1
                
                st.markdown("#### IP별 사용 통계")
                for ip, count in sorted(ip_usage_count.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"**{ip}**: {count}회")
                
                st.markdown("#### 최근 사용 로그")
                for log in usage_logs[-10:]:  # 최근 10개
                    st.write(f"**{log.get('timestamp', 'N/A')}** - IP: {log.get('ip', 'unknown')} - {log.get('details', 'N/A')}")
            else:
                st.info("사용 로그가 없습니다.")
        
        with tab4:
            st.markdown("### 🔐 관리자 로그")
            admin_logs = data.get("admin_logs", [])
            if admin_logs:
                st.markdown("#### 관리자 접속 로그")
                for log in admin_logs[-10:]:  # 최근 10개
                    st.write(f"**{log.get('timestamp', 'N/A')}** - IP: {log.get('ip', 'unknown')} - {log.get('details', 'N/A')}")
            else:
                st.info("관리자 로그가 없습니다.")
        
        with tab5:
            st.markdown("### 💾 로그 관리")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📤 로그 백업")
                if st.button("📥 현재 로그 백업", use_container_width=True):
                    try:
                        # 현재 로그 데이터 백업
                        backup_filename = f"user_logs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        with open(self.db_file, 'r', encoding='utf-8') as f:
                            backup_data = json.load(f)
                        
                        with open(backup_filename, 'w', encoding='utf-8') as f:
                            json.dump(backup_data, f, ensure_ascii=False, indent=2)
                        
                        st.success(f"로그가 {backup_filename}으로 백업되었습니다!")
                        
                        # 다운로드 링크 제공
                        with open(backup_filename, 'rb') as f:
                            st.download_button(
                                label="📥 백업 파일 다운로드",
                                data=f.read(),
                                file_name=backup_filename,
                                mime="application/json"
                            )
                    except Exception as e:
                        st.error(f"백업 중 오류가 발생했습니다: {e}")
            
            with col2:
                st.markdown("#### 📥 로그 복원")
                uploaded_file = st.file_uploader("백업 파일 업로드", type=['json'])
                if uploaded_file is not None:
                    try:
                        # 업로드된 파일 내용 읽기
                        file_content = uploaded_file.read().decode('utf-8')
                        backup_data = json.loads(file_content)
                        
                        # 현재 로그에 백업 데이터 병합
                        if os.path.exists(self.db_file):
                            with open(self.db_file, 'r', encoding='utf-8') as f:
                                current_data = json.load(f)
                        else:
                            current_data = {
                                "users": {},
                                "admin_logs": [],
                                "search_logs": [],
                                "usage_logs": []
                            }
                        
                        # 백업 데이터 병합 (중복 제거)
                        for log_type in ["admin_logs", "search_logs", "usage_logs"]:
                            if log_type in backup_data:
                                for log_entry in backup_data[log_type]:
                                    if log_entry not in current_data[log_type]:
                                        current_data[log_type].append(log_entry)
                        
                        # 병합된 데이터 저장
                        with open(self.db_file, 'w', encoding='utf-8') as f:
                            json.dump(current_data, f, ensure_ascii=False, indent=2)
                        
                        st.success("로그가 성공적으로 복원되었습니다!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"복원 중 오류가 발생했습니다: {e}")
            
            st.markdown("---")
            
            # 로그 파일 목록 표시
            st.markdown("#### 📁 로그 파일 목록")
            try:
                import glob
                log_files = glob.glob("user_logs*.json")
                if log_files:
                    for file in sorted(log_files):
                        file_size = os.path.getsize(file)
                        st.write(f"📄 {file} ({file_size:,} bytes)")
                else:
                    st.info("로그 파일이 없습니다.")
            except Exception as e:
                st.error(f"파일 목록을 불러오는 중 오류가 발생했습니다: {e}")
            
            # 하단 지원 및 문의 안내
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;'>
                <h4>📞 지원 및 문의</h4>
                <p><strong>📬 문의:</strong> GitHub Issues</p>
                <p><strong>💡</strong> 문제 발생, 성능 이슈, 기능 요청이 있으시면 이메일로 연락 주세요.</p>
            </div>
            """, unsafe_allow_html=True)
    
    def show_persona_details(self):
        """페르소나 상세 정보 페이지"""
        st.title("📊 페르소나 상세 정보")
        
        # 뒤로가기 버튼
        if st.button("← 뒤로가기", use_container_width=True):
            st.session_state.show_persona_details = False
            st.rerun()
        
        st.markdown("---")
        
        # 데이터 수집 및 클러스터링 과정 설명
        st.markdown("### 🔬 데이터 수집 및 분석 과정")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            #### 📊 데이터 수집
            - **YouTube API v3**를 사용하여 Gen Z 인플루언서 채널 데이터 수집
            - **STT (Speech-to-Text)** 기술로 비디오 음성을 텍스트로 변환
            - **Whisper AI** 모델을 사용한 고품질 한국어 전사
            - 총 **2914개 파일** (2376개 JSON, 538개 TXT) 수집
            """)
        
        with col2:
            st.markdown("""
            #### 🧠 클러스터링 분석
            - **K-means 클러스터링**으로 유사한 라이프스타일 그룹화
            - **PCA (주성분 분석)**로 차원 축소 및 시각화
            - **키워드 추출** 및 **활동 패턴 분석**
            - **5개 클러스터**로 Gen Z 인플루언서 분류
            """)
        
        st.markdown("---")
        
        # 각 페르소나별 상세 정보
        st.markdown("### 🎭 페르소나별 상세 정보")
        
        for cluster_id, persona in self.personas.items():
            with st.expander(f"{persona['avatar']} {persona['name']} - {persona['description']}", expanded=False):
                
                # 페르소나 기본 정보
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"""
                    **👤 기본 정보**
                    - 이름: {persona['name']}
                    - 나이: {persona.get('age', '정보 없음')}
                    - 성격: {', '.join(persona.get('personality', ['정보 없음']))}
                    - 관심사: {', '.join(persona.get('interests', ['정보 없음']))}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **🎯 전문 분야**
                    - 특기: {persona['specialty']}
                    - 말투: {persona.get('speech_style', '정보 없음')}
                    - 캐치프레이즈: "{persona['catchphrase']}"
                    """)
                
                # 해당 클러스터에 속한 채널 정보
                st.markdown("#### 📺 포함된 채널 정보")
                try:
                    # persona_clusters.csv에서 해당 클러스터의 채널 정보 가져오기
                    import pandas as pd
                    df = pd.read_csv('persona_clusters.csv')
                    cluster_data = df[df['cluster'] == cluster_id]
                    
                    if not cluster_data.empty:
                        st.markdown(f"**총 {len(cluster_data)}개 채널이 이 페르소나에 속합니다:**")
                        
                        # 채널 정보 표시
                        for idx, row in cluster_data.iterrows():
                            video_count = row.get('total_videos', 0) if pd.notna(row.get('total_videos')) else 0
                            stt_count = row.get('total_stt_files', 0) if pd.notna(row.get('total_stt_files')) else 0
                            total_views = row.get('total_views', 0) if pd.notna(row.get('total_views')) else 0
                            
                            st.markdown(f"""
                            - **{row['channel_name']}** (채널 ID: {row['channel_id']})
                              - 영상 수: {video_count:,}개
                              - STT 파일 수: {stt_count:,}개
                              - 총 조회수: {total_views:,}회
                            """)
                    else:
                        st.info("해당 클러스터의 채널 정보를 찾을 수 없습니다.")
                        
                except Exception as e:
                    st.error(f"채널 정보를 불러오는 중 오류가 발생했습니다: {e}")
                
                # 지식 베이스 정보
                st.markdown("#### 🧠 지식 베이스 정보")
                try:
                    chatbot = self.manager.select_chatbot(cluster_id)
                    kb_size = len(chatbot.knowledge_base.get('transcripts', []))
                    top_keywords = list(chatbot.knowledge_base.get('top_keywords', {}).keys())[:10]
                    channel_count = len(chatbot.knowledge_base.get('channels', []))
                    
                    keywords_text = ', '.join(top_keywords) if top_keywords else '정보 없음'
                    
                    st.markdown(f"""
                    - **전사본 수**: {kb_size:,}개
                    - **주요 키워드**: {keywords_text}
                    - **채널 수**: {channel_count}개
                    """)
                except Exception as e:
                    st.error(f"지식 베이스 정보를 불러오는 중 오류가 발생했습니다: {e}")
        
        st.markdown("---")
        
        # 기술 스택 정보
        st.markdown("### 🛠️ 기술 스택")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🤖 AI/ML**
            - OpenAI GPT-4o-mini
            - Whisper STT
            - K-means Clustering
            - PCA 분석
            """)
        
        with col2:
            st.markdown("""
            **🌐 웹 기술**
            - Streamlit
            - Python
            - JSON 데이터 처리
            - 실시간 채팅
            """)
        
        with col3:
            st.markdown("""
            **📊 데이터 분석**
            - Pandas
            - NumPy
            - Scikit-learn
            - 데이터 시각화
            """)
        
        st.markdown("---")
        
        # 프로젝트 정보
        st.markdown("### 📈 프로젝트 통계")
        
        try:
            # 전체 통계 정보
            import pandas as pd
            
            # 채널 통계
            channel_df = pd.read_csv('channel_stats.csv')
            total_channels = len(channel_df)
            total_videos = channel_df['영상수'].sum() if '영상수' in channel_df.columns else 0
            total_stt_files = channel_df['STT파일수'].sum() if 'STT파일수' in channel_df.columns else 0
            total_views = channel_df['총조회수'].sum() if '총조회수' in channel_df.columns else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 채널 수", f"{total_channels:,}개")
            with col2:
                st.metric("총 영상 수", f"{total_videos:,}개")
            with col3:
                st.metric("STT 파일 수", f"{total_stt_files:,}개")
            with col4:
                st.metric("총 조회수", f"{total_views:,}회")
                
        except Exception as e:
            st.error(f"통계 정보를 불러오는 중 오류가 발생했습니다: {e}")
        
        # 하단 지원 및 문의 안내
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;'>
            <h4>📞 지원 및 문의</h4>
            <p><strong>📬 문의:</strong> GitHub Issues</p>
            <p><strong>💡</strong> 문제 발생, 성능 이슈, 기능 요청이 있으시면 이메일로 연락 주세요.</p>
        </div>
        """, unsafe_allow_html=True)
    
    def setup_page_config(self):
        """페이지 설정"""
        st.set_page_config(
            page_title="Gen Z Influencer Persona Bot",
            page_icon="🎭",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def show_sidebar(self):
        """사이드바 표시"""
        with st.sidebar:
            # 홈 버튼
            if st.button("🏠 홈", use_container_width=True, key="home_button"):
                st.session_state.selected_personas = []
                st.session_state.chat_history = []
                st.rerun()
            
            st.markdown("---")
            st.title("🎭 페르소나 선택")
            
            # 다중 페르소나 선택
            st.markdown("### 멀티 채팅")
            if 'selected_personas' not in st.session_state:
                st.session_state.selected_personas = []
            
            for cluster_id, persona in self.personas.items():
                if st.checkbox(f"{persona['avatar']} {persona['name']}", key=f"multi_persona_{cluster_id}"):
                    if cluster_id not in st.session_state.selected_personas:
                        st.session_state.selected_personas.append(cluster_id)
                    # 페르소나 설명 표시
                    st.caption(f"💡 {persona['description']}")
                else:
                    if cluster_id in st.session_state.selected_personas:
                        st.session_state.selected_personas.remove(cluster_id)
            
            if st.button("💬 멀티 채팅 시작", use_container_width=True):
                if st.session_state.selected_personas:
                    st.session_state.chat_history = []
                    st.rerun()
            
            st.markdown("---")
            
            # 다중 페르소나 정보
            if st.session_state.selected_personas:
                st.markdown("### 선택된 페르소나")
                for cluster_id in st.session_state.selected_personas:
                    persona = self.personas[cluster_id]
                    st.markdown(f"**{persona['avatar']} {persona['name']}**")
            
            st.markdown("---")
            
            # 페르소나 상세 정보 링크
            if st.button("📊 페르소나 상세", use_container_width=True):
                st.session_state.show_persona_details = True
                st.rerun()
    
    def show_chat_interface(self):
        """채팅 인터페이스 표시"""
        # 홈 화면
        if not st.session_state.get('selected_personas', []):
            st.title("🏠 Gen Z 인플루언서 페르소나 봇에 오신 것을 환영합니다")
            st.markdown("""
            ### 사용 방법:
            
            **👥 멀티 채팅**: 여러 페르소나를 선택하여 그룹 대화
            - 다양한 인플루언서들의 관점을 얻을 수 있습니다
            - 같은 질문에 대해 다른 페르소나들이 어떻게 답하는지 확인하세요
            - 사이드바에서 여러 페르소나를 선택하고 "멀티 채팅 시작"을 클릭하세요
            
            ### 기능:
            - 📈 **트렌드 분석**: 페르소나별 트렌드 인사이트 제공
            - 🏠 **라이프스타일 가이드**: 전문 분야별 실용적 팁
            - 🎬 **콘텐츠 제작**: 인플루언서 스타일의 콘텐츠 아이디어 생성
            """)
            return
        
        # 다중 페르소나 채팅
        self.show_multi_chat()
    
    def show_single_chat(self):
        """단일 페르소나 채팅"""
        st.title("💬 Single Chat")
        
        # 현재 페르소나 정보
        persona = self.personas[st.session_state.selected_persona]
        chatbot = self.manager.select_chatbot(st.session_state.selected_persona)
        
        # 페르소나 소개
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"<div style='font-size: 4rem; text-align: center;'>{persona['avatar']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            **{persona['name']}** ({persona['description']})
            - Specialty: {persona['specialty']}
            - Catchphrase: "{persona['catchphrase']}"
            """)
        
        st.markdown("---")
        
        # 채팅 기록 표시
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # 채팅 기록 컨테이너
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**👤 You:** {message['content']}")
            else:
                st.markdown(f"**🤖 {persona['name']}:** {message['content']}")
        
        # 메시지 입력
        st.markdown("---")
        user_input = st.text_input("Enter your message:", key="user_input", placeholder="Hello! What are you doing today?")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("📤 Send", use_container_width=True):
                if user_input:
                    self.send_message(user_input, chatbot, persona)
                    st.rerun()
        
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col3:
            if st.button("💾 Save", use_container_width=True):
                self.save_chat_history(persona['name'])
                st.success("Chat history saved!")
    
    def show_multi_chat(self):
        """다중 페르소나 채팅"""
        st.title("👥 멀티 채팅")
        
        # 선택된 페르소나들 표시
        selected_personas = [self.personas[cluster_id] for cluster_id in st.session_state.selected_personas]
        
        cols = st.columns(len(selected_personas))
        for i, persona in enumerate(selected_personas):
            with cols[i]:
                st.markdown(f"<div style='text-align: center;'><div style='font-size: 2rem;'>{persona['avatar']}</div><strong>{persona['name']}</strong></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 채팅 기록 표시
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # 채팅 기록 컨테이너
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**👤 사용자:** {message['content']}")
            else:
                persona_name = message.get('persona', 'Unknown')
                st.markdown(f"**🤖 {persona_name}:** {message['content']}")
        
        # 메시지 입력
        st.markdown("---")
        user_input = st.text_input("메시지를 입력하세요:", key="user_input", placeholder="안녕하세요! 오늘 모두 무엇을 하고 계신가요?")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("📤 모두에게 전송", use_container_width=True):
                if user_input:
                    self.send_multi_message(user_input, selected_personas)
                    st.rerun()
        
        with col2:
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col3:
            if st.button("💾 저장", use_container_width=True):
                self.save_multi_chat_history()
                st.success("멀티 채팅 기록이 저장되었습니다!")
    
    def send_message(self, message, chatbot, persona):
        """메시지 전송"""
        try:
            # 사용자 메시지 추가
            st.session_state.chat_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # 봇 응답 생성
            with st.spinner(f"{persona['name']} is preparing a response..."):
                response = chatbot.chat(message)
            
            # 봇 응답 추가
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        except Exception as e:
            st.error(f"Error sending message: {e}")
    
    def show_trend_analysis(self):
        """트렌드 분석 탭"""
        st.title("📈 트렌드 분석")
        
        # 홈 화면
        if not st.session_state.get('selected_personas', []):
            st.markdown("""
            ### 멀티 트렌드 분석:
            
            **👥 멀티 분석**: 여러 페르소나를 선택하여 다양한 트렌드 인사이트 얻기
            - 같은 트렌드에 대한 서로 다른 관점을 얻을 수 있습니다
            - 다양한 인플루언서들이 현재 트렌드를 어떻게 보는지 비교하세요
            - 사이드바에서 여러 페르소나를 선택하고 "멀티 채팅 시작"을 클릭하세요
            """)
            return
        
        # 다중 페르소나 트렌드 분석
        self.show_multi_trend_analysis()
    
    def show_single_trend_analysis(self):
        """단일 페르소나 트렌드 분석"""
        persona = self.personas[st.session_state.selected_persona]
        chatbot = self.manager.select_chatbot(st.session_state.selected_persona)
        
        # 트렌드 분석 입력
        col1, col2 = st.columns([3, 1])
        with col1:
            trend_topic = st.text_input("Enter a trend topic to analyze:", placeholder="Beauty, Fashion, Cooking, Home Decor, etc.")
        with col2:
            if st.button("🔍 Analyze", use_container_width=True):
                if trend_topic:
                    try:
                        with st.spinner("Analyzing trends..."):
                            analysis = chatbot.get_trend_analysis(trend_topic)
                            
                            st.markdown(f"""
                            **📊 {trend_topic} Trend Analysis**
                            *Analyst: {persona['name']} ({persona['specialty']})*
                            
                            {analysis}
                            """)
                    except Exception as e:
                        st.error(f"Error analyzing trends: {e}")
        
        # 페르소나별 트렌드 인사이트
        st.markdown("### 🎯 Persona-Specific Trends")
        
        trend_insights = {
            0: "Latest trends in cooking, fashion, art, beauty, and travel",
            1: "Home decor, daily life sharing, and pet care trends",
            2: "Reading, journaling, self-development, and tech trends",
            3: "Photography, art, craft, and creative activity trends",
            4: "Beauty, fashion, and styling trends"
        }
        
        st.info(f"💡 {persona['name']}'s expertise: {trend_insights[st.session_state.selected_persona]}")
    
    def show_multi_trend_analysis(self):
        """다중 페르소나 트렌드 분석"""
        selected_personas = [self.personas[cluster_id] for cluster_id in st.session_state.selected_personas]
        
        st.markdown("### 멀티 페르소나 트렌드 분석")
        
        # 선택된 페르소나들 표시
        cols = st.columns(len(selected_personas))
        for i, persona in enumerate(selected_personas):
            with cols[i]:
                st.markdown(f"<div style='text-align: center;'><div style='font-size: 2rem;'>{persona['avatar']}</div><strong>{persona['name']}</strong></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 트렌드 분석 입력
        st.markdown("### 📊 트렌드 분석")
        trend_topic = st.text_input("분석할 트렌드 주제를 입력하세요:", placeholder="뷰티, 패션, 요리, 홈데코 등")
        
        if st.button("🔍 모든 페르소나로 분석", use_container_width=True):
            if trend_topic:
                try:
                    # 검색 로그 기록
                    self.log_user_activity(
                        st.session_state.get('username', 'unknown'), 
                        "search", 
                        f"트렌드 분석: {trend_topic}"
                    )
                    
                    with st.spinner("모든 페르소나가 트렌드를 분석 중..."):
                        for persona in selected_personas:
                            chatbot = self.manager.select_chatbot(list(self.personas.keys())[list(self.personas.values()).index(persona)])
                            
                            # 각 페르소나의 분석을 별도 컨테이너로 표시
                            with st.container():
                                st.markdown(f"### {persona['avatar']} {persona['name']}의 분석")
                                analysis = chatbot.get_trend_analysis(trend_topic)
                                
                                st.markdown(f"""
                                **📊 {trend_topic} 트렌드 분석**
                                *분석가: {persona['name']} ({persona['specialty']})*
                                
                                {analysis}
                                """)
                                st.markdown("---")
                except Exception as e:
                    st.error(f"트렌드 분석 중 오류가 발생했습니다: {e}")
            else:
                st.warning("트렌드 주제를 입력해주세요!")
        
        # 페르소나별 트렌드 인사이트
        st.markdown("### 🎯 멀티 페르소나 전문 분야")
        
        trend_insights = {
            0: "요리, 패션, 예술, 뷰티, 여행의 최신 트렌드",
            1: "홈데코, 일상 공유, 반려동물 케어 트렌드",
            2: "독서, 저널링, 자기계발, 테크 트렌드",
            3: "사진, 예술, 공예, 창작 활동 트렌드",
            4: "뷰티, 패션, 스타일링 트렌드"
        }
        
        for persona in selected_personas:
            cluster_id = list(self.personas.keys())[list(self.personas.values()).index(persona)]
            st.info(f"💡 {persona['name']}의 전문 분야: {trend_insights[cluster_id]}")
    
    def show_lifestyle_guide(self):
        """라이프스타일 가이드 탭"""
        st.title("🏠 라이프스타일 가이드")
        
        # 홈 화면
        if not st.session_state.get('selected_personas', []):
            st.markdown("""
            ### 멀티 라이프스타일 가이드:
            
            **👥 멀티 가이드**: 여러 페르소나를 선택하여 다양한 라이프스타일 팁 얻기
            - 라이프스타일 주제에 대한 서로 다른 관점을 얻을 수 있습니다
            - 다양한 인플루언서들의 팁을 비교하세요
            - 사이드바에서 여러 페르소나를 선택하고 "멀티 채팅 시작"을 클릭하세요
            """)
            return
        
        # 다중 페르소나 라이프스타일 가이드
        self.show_multi_lifestyle_guide()
    
    def show_single_lifestyle_guide(self):
        """단일 페르소나 라이프스타일 가이드"""
        persona = self.personas[st.session_state.selected_persona]
        chatbot = self.manager.select_chatbot(st.session_state.selected_persona)
        
        # 라이프스타일 가이드 생성
        if st.button("💡 Generate Lifestyle Tips", use_container_width=True):
            try:
                with st.spinner(f"Generating {persona['name']}'s lifestyle tips..."):
                    tips = chatbot.get_lifestyle_tips()
                    
                    st.markdown(f"""
                    **🌟 {persona['name']}'s Lifestyle Guide**
                    *Specialty: {persona['specialty']}*
                    
                    {tips}
                    """)
            except Exception as e:
                st.error(f"Error generating lifestyle tips: {e}")
        
        # 페르소나별 특화 가이드
        st.markdown("### 🎯 Specialty Guides")
        
        guide_categories = {
            0: ["Beginner Cooking Recipes", "Fashion Styling Tips", "Art Activity Ideas"],
            1: ["Home Decor Ideas", "Daily Routine Creation", "Pet Care"],
            2: ["Reading Methods", "Journaling Techniques", "Self-Development Plans"],
            3: ["Photography Techniques", "Art Projects", "Creative Cooking"],
            4: ["Beauty Routines", "Fashion Coordination", "Styling Tips"]
        }
        
        categories = guide_categories[st.session_state.selected_persona]
        
        for category in categories:
            if st.button(f"📋 {category}", use_container_width=True):
                try:
                    with st.spinner(f"Generating {category} guide..."):
                        guide = chatbot.chat(f"Please provide a detailed guide for {category}!")
                        
                        st.markdown(f"""
                        **📋 {category}**
                        
                        {guide}
                        """)
                except Exception as e:
                    st.error(f"Error generating guide: {e}")
    
    def show_multi_lifestyle_guide(self):
        """다중 페르소나 라이프스타일 가이드"""
        selected_personas = [self.personas[cluster_id] for cluster_id in st.session_state.selected_personas]
        
        st.markdown("### 멀티 페르소나 라이프스타일 가이드")
        
        # 선택된 페르소나들 표시
        cols = st.columns(len(selected_personas))
        for i, persona in enumerate(selected_personas):
            with cols[i]:
                st.markdown(f"<div style='text-align: center;'><div style='font-size: 2rem;'>{persona['avatar']}</div><strong>{persona['name']}</strong></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 라이프스타일 가이드 생성
        if st.button("💡 모든 페르소나의 라이프스타일 팁 생성", use_container_width=True):
            try:
                with st.spinner("모든 페르소나가 라이프스타일 팁을 생성 중..."):
                    for persona in selected_personas:
                        chatbot = self.manager.select_chatbot(list(self.personas.keys())[list(self.personas.values()).index(persona)])
                        
                        st.markdown(f"### {persona['avatar']} {persona['name']}의 라이프스타일 가이드")
                        tips = chatbot.get_lifestyle_tips()
                        
                        st.markdown(f"""
                        **🌟 {persona['name']}의 라이프스타일 가이드**
                        *전문 분야: {persona['specialty']}*
                        
                        {tips}
                        """)
                        st.markdown("---")
            except Exception as e:
                st.error(f"라이프스타일 팁 생성 중 오류가 발생했습니다: {e}")
        
        # 페르소나별 특화 가이드
        st.markdown("### 🎯 멀티 페르소나 전문 가이드")
        
        guide_categories = {
            0: ["초보자 요리 레시피", "패션 스타일링 팁", "예술 활동 아이디어"],
            1: ["홈데코 아이디어", "일상 루틴 만들기", "반려동물 케어"],
            2: ["독서 방법", "저널링 기법", "자기계발 계획"],
            3: ["사진 촬영 기법", "예술 프로젝트", "창의적 요리"],
            4: ["뷰티 루틴", "패션 코디네이션", "스타일링 팁"]
        }
        
        # 모든 카테고리 수집
        all_categories = set()
        for cluster_id in st.session_state.selected_personas:
            all_categories.update(guide_categories[cluster_id])
        
        for category in sorted(all_categories):
            if st.button(f"📋 {category}", use_container_width=True):
                try:
                    with st.spinner(f"모든 페르소나가 {category} 가이드를 생성 중..."):
                        for persona in selected_personas:
                            chatbot = self.manager.select_chatbot(list(self.personas.keys())[list(self.personas.values()).index(persona)])
                            
                            st.markdown(f"### {persona['avatar']} {persona['name']}의 {category}")
                            guide = chatbot.chat(f"Please provide a detailed guide for {category}!")
                            
                            st.markdown(f"""
                            **📋 {category}**
                            
                            {guide}
                            """)
                            st.markdown("---")
                except Exception as e:
                    st.error(f"가이드 생성 중 오류가 발생했습니다: {e}")
    
    def show_content_creation(self):
        """콘텐츠 제작 탭"""
        st.title("🎬 콘텐츠 제작")
        
        # 홈 화면
        if not st.session_state.get('selected_personas', []):
            st.markdown("""
            ### 멀티 콘텐츠 제작:
            
            **👥 멀티 크리에이터**: 여러 페르소나를 선택하여 다양한 콘텐츠 아이디어 얻기
            - 콘텐츠 제작에 대한 서로 다른 관점을 얻을 수 있습니다
            - 다양한 인플루언서들의 아이디어를 비교하세요
            - 사이드바에서 여러 페르소나를 선택하고 "멀티 채팅 시작"을 클릭하세요
            """)
            return
        
        # 다중 페르소나 콘텐츠 제작
        self.show_multi_content_creation()
    
    def show_single_content_creation(self):
        """단일 페르소나 콘텐츠 제작"""
        persona = self.personas[st.session_state.selected_persona]
        chatbot = self.manager.select_chatbot(st.session_state.selected_persona)
        
        # 콘텐츠 아이디어 생성
        col1, col2 = st.columns([3, 1])
        with col1:
            content_topic = st.text_input("Enter a content topic:", placeholder="Cooking, Fashion, Beauty, Home Decor, etc.")
        with col2:
            if st.button("💡 Generate Ideas", use_container_width=True):
                if content_topic:
                    try:
                        with st.spinner("Generating content ideas..."):
                            idea = chatbot.chat(f"Please provide influencer-style content ideas for {content_topic}!")
                            
                            st.markdown(f"""
                            **🎬 {content_topic} Content Ideas**
                            *Creator: {persona['name']} Style*
                            
                            {idea}
                            """)
                    except Exception as e:
                        st.error(f"Error generating content ideas: {e}")
        
        # 페르소나별 콘텐츠 스타일
        st.markdown("### 🎭 Content Style Guide")
        
        content_styles = {
            0: "All-around content covering various lifestyles",
            1: "Cozy home life and daily sharing content",
            2: "Energetic content about self-development and growth",
            3: "Sophisticated content emphasizing art and creativity",
            4: "Professional content specialized in beauty and fashion"
        }
        
        st.info(f"💡 {persona['name']}'s content style: {content_styles[st.session_state.selected_persona]}")
        
        # 콘텐츠 유형별 아이디어
        st.markdown("### 🎬 Content Type Ideas")
        
        content_types = {
            0: ["Cooking Recipes", "Fashion Styling", "Travel Vlogs", "Art DIY"],
            1: ["Home Decor Tours", "Daily Routines", "Pet Care", "Cozy Life"],
            2: ["Book Reviews", "Journaling Methods", "Self-Development Tips", "Tech Reviews"],
            3: ["Photography", "Art Projects", "Craft DIY", "Creative Cooking"],
            4: ["Beauty Tutorials", "Fashion Coordination", "Styling Tips", "Makeup Reviews"]
        }
        
        types = content_types[st.session_state.selected_persona]
        
        for content_type in types:
            if st.button(f"🎬 {content_type}", use_container_width=True):
                try:
                    with st.spinner(f"Generating {content_type} content ideas..."):
                        idea = chatbot.chat(f"Please provide specific influencer content ideas for {content_type}!")
                        
                        st.markdown(f"""
                        **🎬 {content_type} Content Ideas**
                        
                        {idea}
                        """)
                except Exception as e:
                    st.error(f"Error generating content ideas: {e}")
    
    def show_multi_content_creation(self):
        """다중 페르소나 콘텐츠 제작"""
        selected_personas = [self.personas[cluster_id] for cluster_id in st.session_state.selected_personas]
        
        st.markdown("### 멀티 페르소나 콘텐츠 제작")
        
        # 선택된 페르소나들 표시
        cols = st.columns(len(selected_personas))
        for i, persona in enumerate(selected_personas):
            with cols[i]:
                st.markdown(f"<div style='text-align: center;'><div style='font-size: 2rem;'>{persona['avatar']}</div><strong>{persona['name']}</strong></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 콘텐츠 아이디어 생성
        st.markdown("### 🎬 콘텐츠 아이디어 생성")
        content_topic = st.text_input("콘텐츠 주제를 입력하세요:", placeholder="요리, 패션, 뷰티, 홈데코 등")
        
        if st.button("💡 모든 페르소나의 아이디어 생성", use_container_width=True):
            if content_topic:
                try:
                    with st.spinner("모든 페르소나가 콘텐츠 아이디어를 생성 중..."):
                        for persona in selected_personas:
                            chatbot = self.manager.select_chatbot(list(self.personas.keys())[list(self.personas.values()).index(persona)])
                            
                            # 각 페르소나의 아이디어를 별도 컨테이너로 표시
                            with st.container():
                                st.markdown(f"### {persona['avatar']} {persona['name']}의 콘텐츠 아이디어")
                                idea = chatbot.chat(f"Please provide influencer-style content ideas for {content_topic}!")
                                
                                st.markdown(f"""
                                **🎬 {content_topic} 콘텐츠 아이디어**
                                *크리에이터: {persona['name']} 스타일*
                                
                                {idea}
                                """)
                                st.markdown("---")
                except Exception as e:
                    st.error(f"콘텐츠 아이디어 생성 중 오류가 발생했습니다: {e}")
            else:
                st.warning("콘텐츠 주제를 입력해주세요!")
        
        # 페르소나별 콘텐츠 스타일
        st.markdown("### 🎭 멀티 페르소나 콘텐츠 스타일")
        
        content_styles = {
            0: "다양한 라이프스타일을 다루는 올라운드 콘텐츠",
            1: "아늑한 홈 라이프와 일상 공유 콘텐츠",
            2: "자기계발과 성장에 대한 활기찬 콘텐츠",
            3: "예술과 창의성을 강조하는 세련된 콘텐츠",
            4: "뷰티와 패션에 특화된 전문 콘텐츠"
        }
        
        for persona in selected_personas:
            cluster_id = list(self.personas.keys())[list(self.personas.values()).index(persona)]
            st.info(f"💡 {persona['name']}의 콘텐츠 스타일: {content_styles[cluster_id]}")
        
        # 콘텐츠 유형별 아이디어
        st.markdown("### 🎬 멀티 페르소나 콘텐츠 유형 아이디어")
        
        content_types = {
            0: ["요리 레시피", "패션 스타일링", "여행 브이로그", "예술 DIY"],
            1: ["홈데코 투어", "일상 루틴", "반려동물 케어", "아늑한 라이프"],
            2: ["책 리뷰", "저널링 방법", "자기계발 팁", "테크 리뷰"],
            3: ["사진 촬영", "예술 프로젝트", "공예 DIY", "창의적 요리"],
            4: ["뷰티 튜토리얼", "패션 코디네이션", "스타일링 팁", "메이크업 리뷰"]
        }
        
        # 모든 콘텐츠 유형 수집
        all_content_types = set()
        for cluster_id in st.session_state.selected_personas:
            all_content_types.update(content_types[cluster_id])
        
        for content_type in sorted(all_content_types):
            if st.button(f"🎬 {content_type}", use_container_width=True):
                try:
                    with st.spinner(f"모든 페르소나가 {content_type} 콘텐츠 아이디어를 생성 중..."):
                        for persona in selected_personas:
                            chatbot = self.manager.select_chatbot(list(self.personas.keys())[list(self.personas.values()).index(persona)])
                            
                            st.markdown(f"### {persona['avatar']} {persona['name']}의 {content_type}")
                            idea = chatbot.chat(f"Please provide specific influencer content ideas for {content_type}!")
                            
                            st.markdown(f"""
                            **🎬 {content_type} 콘텐츠 아이디어**
                            
                            {idea}
                            """)
                            st.markdown("---")
                except Exception as e:
                    st.error(f"콘텐츠 아이디어 생성 중 오류가 발생했습니다: {e}")
    
    def send_multi_message(self, message, selected_personas):
        """다중 페르소나에게 메시지 전송"""
        try:
            # 사용자 메시지 추가
            st.session_state.chat_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # 각 페르소나의 응답 생성
            for persona in selected_personas:
                chatbot = self.manager.select_chatbot(list(self.personas.keys())[list(self.personas.values()).index(persona)])
                
                with st.spinner(f"{persona['name']} is responding..."):
                    response = chatbot.chat(message)
                
                # 페르소나 응답 추가
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'persona': persona['name'],
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        except Exception as e:
            st.error(f"Error sending multi message: {e}")
    
    def save_chat_history(self, persona_name):
        """대화 기록 저장"""
        if st.session_state.chat_history:
            try:
                filename = f"chat_history_{persona_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=2)
                st.success(f"Chat history saved to {filename}!")
            except Exception as e:
                st.error(f"Error saving chat history: {e}")
    
    def save_multi_chat_history(self):
        """다중 채팅 기록 저장"""
        if st.session_state.chat_history:
            try:
                persona_names = [self.personas[cluster_id]['name'] for cluster_id in st.session_state.selected_personas]
                filename = f"multi_chat_history_{'_'.join(persona_names).lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=2)
                st.success(f"Multi chat history saved to {filename}!")
            except Exception as e:
                st.error(f"Error saving multi chat history: {e}")
    
    def run(self):
        """메인 실행 함수"""
        try:
            self.setup_page_config()
            
            # 인증 상태 확인
            if not st.session_state.get('authenticated', False):
                self.show_login_page()
                return
            
            # 관리자 모드
            if st.session_state.get('user_type') == 'admin':
                self.show_admin_dashboard()
                return
            
            # 페르소나 상세 정보 페이지
            if st.session_state.get('show_persona_details', False):
                self.show_persona_details()
                return
            
            # 일반 사용자 모드
            # 헤더
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 2rem;'>
                <p style='font-size: 0.8rem; margin-bottom: 0.5rem; opacity: 0.8;'>Gen Z Influencer Persona Bot</p>
                <h1>🎭 Gen Z Influencer Persona Bot</h1>
                <p>Chat with Gen Z influencers, analyze trends, and get lifestyle guides!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 사용자 정보 표시
            st.sidebar.markdown(f"**👤 로그인된 사용자:** {st.session_state.get('username', 'Unknown')}")
            if st.sidebar.button("🚪 로그아웃", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_type = None
                st.session_state.username = None
                st.rerun()
            
            # 사이드바
            self.show_sidebar()
            
            # 메인 탭
            tab1, tab2, tab3, tab4 = st.tabs(["💬 채팅", "📈 트렌드 분석", "🏠 라이프스타일 가이드", "🎬 콘텐츠 제작"])
            
            with tab1:
                self.show_chat_interface()
            
            with tab2:
                self.show_trend_analysis()
            
            with tab3:
                self.show_lifestyle_guide()
            
            with tab4:
                self.show_content_creation()
            
            # 하단 지원 및 문의 안내
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;'>
                <h4>📞 지원 및 문의</h4>
                <p><strong>📬 문의:</strong> GitHub Issues</p>
                <p><strong>💡</strong> 문제 발생, 성능 이슈, 기능 요청이 있으시면 이메일로 연락 주세요.</p>
            </div>
            """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Application error: {e}")
            st.error("Please check if OpenAI API key is set.")

# 실행
if __name__ == "__main__":
    try:
        # 환경 변수 확인
        if not os.getenv('OPENAI_API_KEY'):
            print("Warning: OPENAI_API_KEY not set. Some features may not work.")
        
        gui = EnglishPersonaGUI()
        gui.run()
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Please check if OpenAI API key is set.")
        import traceback
        traceback.print_exc()
