# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import glob
from collections import Counter, defaultdict
from datetime import datetime
from openai import OpenAI

# ============================================================================
# 페이지 설정
# ============================================================================
st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 전문적인 CSS 스타일링
# ============================================================================
st.markdown("""
<style>
    /* 전체 배경 - 흰색 통일 */
    .main {
        background-color: #ffffff;
    }
    
    .stApp {
        background-color: #ffffff;
    }
    
    /* 블록 컨테이너 배경 */
    .block-container {
        background-color: #ffffff;
        padding-top: 2rem;
    }
    
    /* 헤더 스타일 */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* 모든 텍스트 색상을 명확하게 */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
    [data-testid="stMarkdownContainer"], 
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] div,
    .stText, p, span, div, label {
        color: #1a1a1a !important;
    }
    
    /* 헤더 색상 */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #2c3e50 !important;
    }
    
    /* 메트릭 카드 */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
        color: #2c3e50 !important;
        background-color: transparent !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 500;
        color: #5a6c7d !important;
        background-color: transparent !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #16a085 !important;
    }
    
    /* 메트릭 컨테이너 */
    [data-testid="metric-container"] {
        background-color: #f8f9fb !important;
        border: 1px solid #e1e4e8 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
        background-color: #f8f9fb !important;
        border: 1px solid #e1e4e8 !important;
        border-radius: 8px;
        font-weight: 500;
        color: #2c3e50 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* 탭 패널 배경 */
    [data-baseweb="tab-panel"] {
        background-color: #ffffff !important;
    }
    
    /* 사이드바 - 다크 테마 */
    [data-testid="stSidebar"] {
        background-color: #2c3e50;
    }
    
    [data-testid="stSidebar"] * {
        color: #ecf0f1 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    /* 버튼 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 검색창 */
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 2px solid #d0d7de;
        padding: 0.5rem 1rem;
        color: #2c3e50 !important;
        background-color: #ffffff !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background-color: #ffffff !important;
    }
    
    .stTextInput label {
        color: #2c3e50 !important;
        font-weight: 500;
    }
    
    /* Select box */
    .stSelectbox > div > div > div {
        color: #2c3e50 !important;
        background-color: white !important;
    }
    
    .stSelectbox label {
        color: #2c3e50 !important;
        font-weight: 500;
    }
    
    /* Radio buttons */
    .stRadio > div {
        color: #2c3e50 !important;
    }
    
    .stRadio label {
        color: #2c3e50 !important;
        font-weight: 500;
    }
    
    /* Checkbox - 보라색 테마 */
    .stCheckbox {
        color: #2c3e50 !important;
    }
    
    .stCheckbox label {
        color: #2c3e50 !important;
        font-weight: 500;
    }
    
    .stCheckbox > label > div {
        color: #2c3e50 !important;
    }
    
    /* Checkbox input 스타일 */
    input[type="checkbox"] {
        accent-color: #667eea !important;
        width: 18px;
        height: 18px;
        cursor: pointer;
    }
    
    /* Caption 색상 */
    .stCaption {
        color: #7f8c8d !important;
    }
    
    /* Info/Warning/Success 박스 */
    .stAlert {
        border-radius: 8px;
        background-color: #ffffff !important;
        border: 1px solid #e1e4e8 !important;
    }
    
    /* Info 박스 */
    [data-baseweb="notification"] {
        background-color: #eff6ff !important;
        border-left: 4px solid #3b82f6 !important;
    }
    
    /* Expander */
    .stExpander {
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        background-color: #f8f9fb !important;
    }
    
    .stExpander summary {
        color: #2c3e50 !important;
        font-weight: 600;
        background-color: #f8f9fb !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        background-color: #ffffff !important;
        border: 1px solid #e1e4e8 !important;
        border-radius: 8px;
    }
    
    /* Form 요소 전반적인 스타일 */
    .stForm {
        border: none;
        background-color: transparent;
    }
    
    /* 텍스트 영역 */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #d0d7de;
        color: #2c3e50 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 데이터 로딩
# ============================================================================
@st.cache_data(show_spinner=False)
def load_database():
    """데이터베이스 로드 및 전처리"""
    videos = []
    data_dir = 'youtube_data'
    
    if not os.path.exists(data_dir):
        return []
    
    for channel_dir in os.listdir(data_dir):
        channel_path = os.path.join(data_dir, channel_dir)
        if not os.path.isdir(channel_path):
            continue
        
        # 채널 정보
        channel_name = channel_dir
        channel_info_path = os.path.join(channel_path, 'channel_info.json')
        
        if os.path.exists(channel_info_path):
            try:
                with open(channel_info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    channel_name = info.get('channel_title', channel_dir)
            except:
                pass
        
        # 영상 데이터
        for json_file in glob.glob(os.path.join(channel_path, '*.json')):
            if 'channel_info' in json_file:
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    video = json.load(f)
                
                # 메타데이터 정규화
                video['channel_name'] = channel_name
                video['channel_id'] = channel_dir
                
                # 텍스트 처리
                full_text = ""
                if video.get('transcript'):
                    full_text = " ".join([seg.get('text', '') for seg in video['transcript']])
                
                video['full_text'] = full_text
                video['has_text'] = len(full_text) > 0
                
                # 조회수 정수 변환
                try:
                    video['view_count_int'] = int(video['metadata'].get('view_count', 0))
                except:
                    video['view_count_int'] = 0
                
                videos.append(video)
            except:
                continue
    
    return videos

# ============================================================================
# 유틸리티 함수
# ============================================================================
def search_videos(videos, keyword):
    """키워드 검색"""
    keyword_lower = keyword.lower()
    results = []
    
    for video in videos:
        if not video.get('has_text'):
            continue
        
        if keyword_lower in video['full_text'].lower():
            count = video['full_text'].lower().count(keyword_lower)
            
            # 매칭 세그먼트
            matching_segs = []
            for seg in video.get('transcript', []):
                if keyword_lower in seg.get('text', '').lower():
                    matching_segs.append(seg)
            
            results.append({
                **video,
                'match_count': count,
                'matching_segments': matching_segs[:5]  # 상위 5개만
            })
    
    return sorted(results, key=lambda x: x['match_count'], reverse=True)

def format_number(num):
    """숫자 포맷팅"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def get_smartphone_videos(videos):
    """스마트폰 관련 영상 필터링"""
    keywords = ['smartphone', 'iphone', 'galaxy', 'android', 'phone',
               'imessage', 'facetime', 'airpods', 'case',
               '스마트폰', '아이폰', '갤럭시', '핸드폰', '케이스']
    
    results = []
    for video in videos:
        if not video.get('has_text'):
            continue
        
        text_lower = video['full_text'].lower()
        if any(kw.lower() in text_lower for kw in keywords):
            results.append(video)
    
    return results

# ============================================================================
# 인증 시스템
# ============================================================================
def check_authentication():
    """로그인 확인"""
    
    # 세션 상태 초기화
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # 이미 인증됨
    if st.session_state.authenticated:
        return True
    
    # 로그인 페이지
    st.markdown("""
    <div class="dashboard-header">
        <h1 style='margin:0; font-size: 2.5rem;'>🔐 YouTube Analytics Dashboard</h1>
        <p style='margin:0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;'>Gen Z Influencer Content Analysis</p>
        <p style='margin:0.5rem 0 0 0; opacity: 0.8; font-size: 0.95rem;'>로그인이 필요합니다</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 로그인 폼
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 로그인")
        
        with st.form("login_form"):
            username = st.text_input("아이디", placeholder="아이디를 입력하세요")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            submit = st.form_submit_button("로그인", use_container_width=True)
            
            if submit:
                # 인증 확인
                if username == "myproject" and password == "sangin.chun":
                    st.session_state.authenticated = True
                    st.success("✅ 로그인 성공!")
                    st.rerun()
                else:
                    st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")
    
    return False

# ============================================================================
# 메인 앱
# ============================================================================
def main():
    # 인증 확인
    if not check_authentication():
        return
    
    # 헤더
    st.markdown("""
    <div class="dashboard-header">
        <h1 style='margin:0; font-size: 2.5rem;'>📊 YouTube Analytics Dashboard</h1>
        <p style='margin:0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;'>Gen Z Influencer Content Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 데이터 로드
    with st.spinner('🔄 데이터 로딩 중...'):
        videos = load_database()
    
    if not videos:
        st.error("❌ 데이터를 찾을 수 없습니다. youtube_data 폴더를 확인하세요.")
        st.stop()
    
    # 기본 데이터 준비
    videos_with_text = [v for v in videos if v.get('has_text')]
    smartphone_videos = get_smartphone_videos(videos)
    
    # ========================================================================
    # 사이드바
    # ========================================================================
    with st.sidebar:
        # 로그아웃 버튼
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📊 데이터 개요")
        st.metric("총 영상", f"{len(videos):,}")
        st.metric("자막/STT", f"{len(videos_with_text):,}")
        st.metric("채널 수", f"{len(set(v['channel_id'] for v in videos))}")
        
        st.markdown("---")
        
        st.markdown("### 🔧 필터")
        
        # 채널 필터
        all_channels = ["전체"] + sorted(list(set(v['channel_name'] for v in videos)))
        selected_channel = st.selectbox("채널 선택", all_channels)
        
        # 자막 필터
        transcript_filter = st.radio(
            "자막 필터",
            ["전체", "자막/STT 있음", "메타데이터만"]
        )
        
        st.markdown("---")
        st.caption(f"📅 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 필터 적용
    filtered_videos = videos.copy()
    
    if selected_channel != "전체":
        filtered_videos = [v for v in filtered_videos if v['channel_name'] == selected_channel]
    
    if transcript_filter == "자막/STT 있음":
        filtered_videos = [v for v in filtered_videos if v.get('has_text')]
    elif transcript_filter == "메타데이터만":
        filtered_videos = [v for v in filtered_videos if not v.get('has_text')]
    
    # ========================================================================
    # 탭 구성
    # ========================================================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 대시보드",
        "🔍 키워드 분석",
        "📱 스마트폰 인사이트",
        "🎯 상세 데이터",
        "🤖 AI 보고서"
    ])
    
    # ========================================================================
    # 탭 1: 대시보드
    # ========================================================================
    with tab1:
        # KPI 메트릭
        st.markdown("### 📊 주요 지표")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "총 영상",
                f"{len(filtered_videos):,}",
                delta=f"{len(filtered_videos) - len(videos)}" if selected_channel != "전체" else None
            )
        
        with col2:
            text_count = len([v for v in filtered_videos if v.get('has_text')])
            st.metric("자막/STT", f"{text_count:,}")
        
        with col3:
            total_views = sum(v['view_count_int'] for v in filtered_videos)
            st.metric("총 조회수", format_number(total_views))
        
        with col4:
            avg_views = total_views / len(filtered_videos) if filtered_videos else 0
            st.metric("평균 조회수", format_number(int(avg_views)))
        
        with col5:
            smartphone_count = len([v for v in filtered_videos 
                                   if v.get('has_text') and 
                                   any(kw in v['full_text'].lower() 
                                       for kw in ['iphone', 'phone', 'smartphone', '아이폰', '폰'])])
            st.metric("스마트폰 관련", f"{smartphone_count}")
        
        st.markdown("---")
        
        # 시각화
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📺 채널별 영상 분포")
            
            channel_counts = Counter(v['channel_name'] for v in filtered_videos)
            df_channels = pd.DataFrame(
                channel_counts.most_common(15),
                columns=['채널', '영상 수']
            )
            
            fig = px.bar(
                df_channels,
                x='영상 수',
                y='채널',
                orientation='h',
                color='영상 수',
                color_continuous_scale='Purples',
                text='영상 수'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                height=500,
                showlegend=False,
                xaxis_title="",
                yaxis_title="",
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📝 자막 수집 현황")
            
            types = Counter(v.get('transcript_type') for v in filtered_videos)
            
            type_map = {
                'subtitle': '📄 수동 자막',
                'auto-generated': '🤖 자동 생성',
                'whisper-stt': '🎙️ Whisper STT',
                'none': '❌ 없음',
                None: '❌ 없음'
            }
            
            df_types = pd.DataFrame([
                {'타입': type_map.get(k, k), '개수': v}
                for k, v in types.items()
            ])
            
            colors = ['#667eea', '#764ba2', '#f093fb', '#e0e0e0']
            
            fig = px.pie(
                df_types,
                values='개수',
                names='타입',
                color_discrete_sequence=colors,
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=500, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # 조회수 분석
        st.markdown("### 👁️ 조회수 분석")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 조회수 분포 히스토그램
            view_counts = [v['view_count_int'] for v in filtered_videos if v['view_count_int'] > 0]
            
            if view_counts:
                df_views = pd.DataFrame({'조회수': view_counts})
                
                fig = px.histogram(
                    df_views,
                    x='조회수',
                    nbins=30,
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(
                    height=300,
                    xaxis_title="조회수",
                    yaxis_title="영상 수",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if view_counts:
                st.markdown("#### 📊 통계")
                st.metric("최고", f"{max(view_counts):,}")
                st.metric("평균", f"{sum(view_counts)//len(view_counts):,}")
                st.metric("중앙값", f"{sorted(view_counts)[len(view_counts)//2]:,}")
                st.metric("최저", f"{min(view_counts):,}")
    
    # ========================================================================
    # 탭 2: 키워드 분석
    # ========================================================================
    with tab2:
        st.markdown("### 🔍 키워드 검색 & 분석")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            search_keyword = st.text_input(
                "",
                placeholder="🔍 검색어를 입력하세요 (예: iPhone, 배터리, 케이스)",
                label_visibility="collapsed"
            )
        
        with col2:
            search_btn = st.button("검색", use_container_width=True, type="primary")
        
        if search_keyword:
            with st.spinner(f"'{search_keyword}' 검색 중..."):
                results = search_videos(videos_with_text, search_keyword)
            
            if results:
                total_mentions = sum(r['match_count'] for r in results)
                
                # 검색 결과 요약
                col1, col2, col3 = st.columns(3)
                col1.metric("발견 영상", f"{len(results)}개")
                col2.metric("총 언급", f"{total_mentions}회")
                col3.metric("평균 언급", f"{total_mentions/len(results):.1f}회")
                
                st.markdown("---")
                
                # 채널별 분포
                st.markdown("#### 📊 채널별 언급 분포")
                
                channel_mentions = defaultdict(int)
                for r in results:
                    channel_mentions[r['channel_name']] += r['match_count']
                
                df_channel_mentions = pd.DataFrame(
                    sorted(channel_mentions.items(), key=lambda x: x[1], reverse=True)[:10],
                    columns=['채널', '언급 횟수']
                )
                
                fig = px.bar(
                    df_channel_mentions,
                    x='언급 횟수',
                    y='채널',
                    orientation='h',
                    color='언급 횟수',
                    color_continuous_scale='Viridis',
                    text='언급 횟수'
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # 검색 결과 리스트
                st.markdown("#### 🎬 검색 결과")
                
                for idx, result in enumerate(results[:15], 1):
                    with st.container():
                        col1, col2 = st.columns([5, 1])
                        
                        with col1:
                            st.markdown(f"**{idx}. {result['metadata']['title']}**")
                            st.caption(f"📺 {result['channel_name']} | 🔗 {result['metadata']['video_url']}")
                        
                        with col2:
                            st.metric("", f"{result['match_count']}회", label_visibility="collapsed")
                        
                        # 언급 내용 미리보기
                        if result['matching_segments']:
                            seg = result['matching_segments'][0]
                            ts = seg.get('start', 0)
                            m, s = int(ts // 60), int(ts % 60)
                            st.info(f"⏱️ [{m:02d}:{s:02d}] {seg.get('text', '')[:120]}...")
                        
                        st.markdown("---")
                
                if len(results) > 15:
                    st.info(f"💡 {len(results) - 15}개 영상 더 있음 (상위 15개만 표시)")
            else:
                st.warning(f"'{search_keyword}'를 찾을 수 없습니다.")
    
    # ========================================================================
    # 탭 3: 스마트폰 인사이트
    # ========================================================================
    with tab3:
        st.markdown("### 📱 스마트폰 관련 콘텐츠 인사이트")
        
        smartphone_vids = [v for v in filtered_videos if v in smartphone_videos]
        
        if not smartphone_vids:
            st.warning("스마트폰 관련 영상이 없습니다.")
        else:
            # 요약 메트릭
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("스마트폰 관련 영상", f"{len(smartphone_vids)}개")
            
            with col2:
                rate = len(smartphone_vids) / len(videos_with_text) * 100 if videos_with_text else 0
                st.metric("전체 대비 비율", f"{rate:.1f}%")
            
            with col3:
                total_views = sum(v['view_count_int'] for v in smartphone_vids)
                st.metric("총 조회수", format_number(total_views))
            
            st.markdown("---")
            
            # 토픽 분석
            st.markdown("### 🏷️ 주요 토픽 분포")
            
            topics = {
                '🎨 케이스/액세서리': ['case', 'accessories', 'airpods', 'screen protector', '케이스'],
                '🔋 배터리/충전': ['battery', 'charging', 'charger', '배터리', '충전'],
                '📸 촬영/카메라': ['camera', 'selfie', 'photo', '카메라', '셀카'],
                '📲 앱/소프트웨어': ['app', 'ios', 'android', 'widget', '앱'],
                '📱 디지털 웰빙': ['screen time', 'notification', '스크린타임', '알림'],
                '📦 언박싱/리뷰': ['unboxing', 'review', 'new phone', '언박싱', '리뷰'],
                '💬 메시징/통화': ['imessage', 'facetime', 'message', '메시지', '통화']
            }
            
            topic_counts = {}
            for topic, keywords in topics.items():
                count = sum(1 for v in smartphone_vids 
                          if any(kw.lower() in v['full_text'].lower() for kw in keywords))
                topic_counts[topic] = count
            
            df_topics = pd.DataFrame(
                sorted(topic_counts.items(), key=lambda x: x[1], reverse=True),
                columns=['토픽', '영상 수']
            )
            
            fig = px.bar(
                df_topics,
                x='영상 수',
                y='토픽',
                orientation='h',
                color='영상 수',
                color_continuous_scale='Plasma',
                text='영상 수'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # 채널별 스마트폰 콘텐츠
            st.markdown("### 📺 채널별 스마트폰 콘텐츠")
            
            channel_smartphone = Counter(v['channel_name'] for v in smartphone_vids)
            df_ch_phone = pd.DataFrame(
                channel_smartphone.most_common(10),
                columns=['채널', '영상 수']
            )
            
            fig = px.bar(
                df_ch_phone,
                x='영상 수',
                y='채널',
                orientation='h',
                color='영상 수',
                color_continuous_scale='Oranges',
                text='영상 수'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # 탭 4: 상세 데이터
    # ========================================================================
    with tab4:
        st.markdown("### 🎯 상세 영상 데이터")
        
        # 정렬 옵션
        sort_option = st.selectbox(
            "정렬 기준",
            ["조회수 높은 순", "조회수 낮은 순", "제목 가나다순"]
        )
        
        sorted_vids = filtered_videos.copy()
        
        if sort_option == "조회수 높은 순":
            sorted_vids.sort(key=lambda x: x['view_count_int'], reverse=True)
        elif sort_option == "조회수 낮은 순":
            sorted_vids.sort(key=lambda x: x['view_count_int'])
        elif sort_option == "제목 가나다순":
            sorted_vids.sort(key=lambda x: x['metadata']['title'])
        
        st.markdown("---")
        
        # 테이블 형식으로 표시
        for idx, video in enumerate(sorted_vids[:30], 1):
            meta = video['metadata']
            
            col1, col2, col3 = st.columns([6, 2, 1])
            
            with col1:
                st.markdown(f"**{idx}. {meta['title']}**")
                st.caption(f"📺 {video['channel_name']}")
            
            with col2:
                st.write(f"👁️ {video['view_count_int']:,}")
                st.caption(f"❤️ {meta.get('like_count', 0)} | 💬 {meta.get('comment_count', 0)}")
            
            with col3:
                has_text = "✅" if video.get('has_text') else "❌"
                st.write(has_text)
                st.caption("자막")
            
            with st.container():
                st.caption(f"🔗 {meta['video_url']}")
            
            st.markdown("---")
        
        if len(sorted_vids) > 30:
            st.info(f"💡 {len(sorted_vids) - 30}개 영상 더 있음")
    
    # ========================================================================
    # 탭 5: AI 보고서
    # ========================================================================
    with tab5:
        st.markdown("### 🤖 AI 기반 데이터 분석 & 보고서 생성")
        
        # 예상 비용 표시
        text_videos_count = len([v for v in filtered_videos if v.get('has_text')])
        
        # 세션 상태에 모델 선택 저장
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = "GPT-4o (고품질)"
        
        # 모델 선택
        st.markdown("#### 🤖 AI 모델 선택")
        model_option = st.radio(
            "모델",
            options=["GPT-4o-mini (빠르고 저렴)", "GPT-4o (고품질)"],
            index=0,
            horizontal=True,
            key="model_selection",
            label_visibility="collapsed"
        )
        
        # 모델별 비용 계산
        if "mini" in model_option:
            # GPT-4o-mini: Input $0.150/1M, Output $0.600/1M
            cost_general = 10  # ~₩10
            cost_sample = 20   # ~₩20
            cost_full = int(text_videos_count / 50 * 20)
            model_name = "gpt-4o-mini"
            model_desc = "16배 저렴, 빠른 속도"
        else:
            # GPT-4o: Input $2.50/1M, Output $10.00/1M
            cost_general = 33  # ~₩33
            cost_sample = 170  # ~₩170
            cost_full = int(text_videos_count / 50 * 170)
            model_name = "gpt-4o"
            model_desc = "최고 품질"
        
        # 예상 비용 카드 (Streamlit 네이티브 컴포넌트 사용)
        st.markdown(f"### 💰 예상 비용 안내 - {model_option}")
        st.caption(f"현재 필터링된 영상: **{len(filtered_videos)}개** (텍스트 있음: **{text_videos_count}개**)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="💬 일반 모드",
                value=f"~₩{cost_general}",
                delta="통계 요약만"
            )
        
        with col2:
            st.metric(
                label="📄 상세 (샘플 50개)",
                value=f"~₩{cost_sample}",
                delta="대표 샘플 분석"
            )
        
        with col3:
            st.metric(
                label="📊 전체 데이터",
                value=f"~₩{cost_full:,}",
                delta=f"{text_videos_count}개 모두"
            )
        
        st.caption(f"ⓘ {model_desc} | $1 = ₩1,330 기준, 실제 비용은 텍스트 길이에 따라 변동")
        st.markdown("---")
        
        # API 키 설정 (환경변수에서 가져오기)
        # Streamlit Cloud에서 Secrets로 설정 필요
        api_key_default = os.environ.get('OPENAI_API_KEY', '')
        
        # Streamlit Secrets 확인 (Cloud 배포 시)
        try:
            if not api_key_default and hasattr(st, 'secrets'):
                api_key_default = st.secrets.get('OPENAI_API_KEY', '')
        except:
            pass
        
        with st.expander("⚙️ API 설정 (선택사항)", expanded=False):
            api_key_input = st.text_input(
                "OpenAI API 키 (기본값 설정됨)",
                value=api_key_default if api_key_default else "",
                type="password",
                help="기본 API 키가 설정되어 있습니다. 다른 키를 사용하려면 입력하세요.",
                key="openai_api_key_input"
            )
            
            api_key = api_key_input if api_key_input else api_key_default
            
            if api_key:
                st.success("✅ API 키가 설정되었습니다! 바로 질문하세요.")
            else:
                st.warning("⚠️ API 키를 입력하세요")
        
        st.markdown("---")
        
        # 데이터 컨텍스트 생성
        def create_data_context(videos_data, include_full_text=False, sample_size=50):
            """분석을 위한 데이터 요약 생성"""
            context = f"""
# 데이터 개요
- 총 영상 수: {len(videos_data)}개
- 자막/STT 있음: {len([v for v in videos_data if v.get('has_text')])}개
- 총 채널 수: {len(set(v['channel_id'] for v in videos_data))}개

# 채널별 영상 수
"""
            channel_counts = Counter(v['channel_name'] for v in videos_data)
            for channel, count in channel_counts.most_common(10):
                context += f"- {channel}: {count}개\n"
            
            context += "\n# 스마트폰 관련 콘텐츠\n"
            smartphone_vids = get_smartphone_videos(videos_data)
            context += f"- 총 {len(smartphone_vids)}개 영상에서 스마트폰 관련 내용 발견\n"
            
            # 조회수 통계
            total_views = sum(v['view_count_int'] for v in videos_data)
            avg_views = total_views / len(videos_data) if videos_data else 0
            context += f"\n# 조회수 통계\n"
            context += f"- 총 조회수: {total_views:,}\n"
            context += f"- 평균 조회수: {avg_views:,.0f}\n"
            
            # 실제 텍스트 샘플 포함 (상세 보고서용)
            if include_full_text:
                context += "\n\n" + "="*80 + "\n"
                context += f"# 실제 영상 텍스트 데이터 ({sample_size if sample_size > 0 else '전체'})\n"
                context += "="*80 + "\n\n"
                
                # 텍스트가 있는 영상들만 필터링
                text_videos = [v for v in videos_data if v.get('has_text')]
                
                # 샘플 크기에 따라 선택 (0이면 전체)
                videos_to_include = text_videos if sample_size <= 0 else text_videos[:sample_size]
                
                for idx, video in enumerate(videos_to_include, 1):
                    meta = video['metadata']
                    context += f"\n[{idx}] 채널: {video['channel_name']}\n"
                    context += f"    영상: {meta['title']}\n"
                    context += f"    조회수: {meta['view_count']}\n"
                    context += f"    자막 타입: {video.get('transcript_type', 'N/A')}\n"
                    
                    # 전체 텍스트 포함 (길이 제한)
                    full_text = video.get('full_text', '')
                    if len(full_text) > 2000:
                        context += f"    내용 (일부): {full_text[:2000]}...\n"
                    else:
                        context += f"    내용: {full_text}\n"
                    context += "\n" + "-"*80 + "\n"
                
                context += f"\n\n분석에 사용된 영상: {len(videos_to_include)}개 / 전체 {len(text_videos)}개\n"
            
            return context
        
        # AI 분석 함수
        def analyze_with_ai(question, api_key, data_context, chat_history=[], detailed_report=False, model="gpt-4o"):
            """ChatGPT API를 사용한 데이터 분석"""
            try:
                client = OpenAI(api_key=api_key)
                
                # 상세 보고서용 추가 지시사항
                detailed_instructions = ""
                if detailed_report:
                    detailed_instructions = """

**상세 보고서 작성 가이드:**
- 토픽별로 구분하여 체계적으로 정리
- 각 토픽마다 언급 횟수 집계
- 실제 영상 예시를 최소 5개 이상 포함
- 채널명, 영상 제목, 조회수, 구체적인 내용 인용
- 키워드별 분류 및 트렌드 분석
- 통계와 인사이트를 풍부하게 제공
- 마크다운 형식으로 보기 좋게 구조화"""
                
                # 시스템 메시지
                system_msg = f"""당신은 YouTube 영상 데이터 분석 전문가입니다.
아래 데이터를 기반으로 사용자의 질문에 답변하세요.

{data_context}

분석 시 주의사항:
1. 실제 데이터에 없는 내용은 추측하지 마세요
2. 구체적인 숫자와 예시를 들어 설명하세요
3. 한국어로 전문적이면서도 이해하기 쉽게 답변하세요
4. 필요시 요약, 통계, 트렌드를 제시하세요
5. 실제 영상 제목, 채널명, 조회수 등 구체적인 정보를 인용하세요{detailed_instructions}"""
                
                # 메시지 구성
                messages = [{"role": "system", "content": system_msg}]
                
                # 대화 히스토리 추가
                for msg in chat_history:
                    messages.append(msg)
                
                # 현재 질문 추가
                messages.append({"role": "user", "content": question})
                
                # API 호출 (상세 보고서는 더 긴 응답)
                max_tokens = 4000 if detailed_report else 2000
                
                response = client.chat.completions.create(
                    model=model,  # 선택된 모델 사용
                    messages=messages,
                    temperature=0.7,
                    max_tokens=max_tokens
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                return f"❌ 에러 발생: {str(e)}\n\nAPI 키를 확인하거나 OpenAI 크레딧을 확인하세요."
        
        # 세션 상태 초기화
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'report_content' not in st.session_state:
            st.session_state.report_content = ""
        
        # 채팅 인터페이스
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_question = st.text_input(
                "질문",
                placeholder="예: 스마트폰 관련 영상이 많은 채널 Top 5는? 아이폰과 관련된 주요 토픽은?",
                key="ai_question_input",
                label_visibility="collapsed"
            )
        
        with col2:
            analyze_btn = st.button("분석 요청", use_container_width=True, type="primary", key="analyze_btn")
        
        # 상세 보고서 옵션
        col1, col2 = st.columns([1, 1])
        
        with col1:
            detailed_report_mode = st.checkbox(
                "📄 상세 보고서 모드",
                help="체크하면 실제 영상 텍스트를 포함하여 상세 보고서를 생성합니다",
                key="detailed_report_checkbox"
            )
        
        with col2:
            if detailed_report_mode:
                data_scope = st.radio(
                    "데이터 범위",
                    options=["샘플 50개 (~₩170)", f"전체 {text_videos_count}개 (~₩{int(text_videos_count / 50 * 170):,})"],
                    index=0,
                    key="data_scope_radio",
                    horizontal=True
                )
                use_full_data = "전체" in data_scope
            else:
                use_full_data = False
        
        # 예시 질문 버튼
        st.markdown("**💡 예시 질문:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 채널별 특징 분석", key="q1"):
                user_question = "각 채널별로 어떤 특징이 있나요? 주요 채널들의 콘텐츠 성향을 분석해주세요."
                analyze_btn = True
        
        with col2:
            if st.button("📱 스마트폰 트렌드", key="q2"):
                user_question = "스마트폰 관련 콘텐츠에서 어떤 트렌드가 보이나요?"
                analyze_btn = True
        
        with col3:
            if st.button("🔥 인기 콘텐츠 분석", key="q3"):
                user_question = "조회수가 높은 영상들의 공통점은 무엇인가요?"
                analyze_btn = True
        
        st.markdown("---")
        
        # 분석 실행
        if (user_question and analyze_btn) or (user_question and st.session_state.get('auto_analyze')):
            if not api_key:
                st.error("⚠️ OpenAI API 키를 먼저 입력하세요!")
            else:
                # 스피너 텍스트 설정
                if detailed_report_mode and use_full_data:
                    spinner_text = f"📊 전체 {text_videos_count}개 영상 데이터를 분석하고 있습니다... (예상 시간: 30-60초)"
                    sample_size = 0  # 0이면 전체
                elif detailed_report_mode:
                    spinner_text = "📄 상세 보고서를 생성하고 있습니다... (샘플 50개 분석 중)"
                    sample_size = 50
                else:
                    spinner_text = "🤖 AI가 데이터를 분석하고 있습니다..."
                    sample_size = 50
                
                with st.spinner(spinner_text):
                    # 데이터 컨텍스트 생성 (상세 보고서 모드면 실제 텍스트 포함)
                    data_context = create_data_context(
                        filtered_videos, 
                        include_full_text=detailed_report_mode,
                        sample_size=sample_size
                    )
                    
                    # AI 분석 (선택된 모델 사용)
                    response = analyze_with_ai(
                        user_question,
                        api_key,
                        data_context,
                        st.session_state.chat_history,
                        detailed_report=detailed_report_mode,
                        model=model_name
                    )
                    
                    # 대화 히스토리 저장
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_question
                    })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    # 보고서에 추가
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if detailed_report_mode and use_full_data:
                        report_mode = f" [상세 보고서 - 전체 {text_videos_count}개 - {model_name.upper()}]"
                    elif detailed_report_mode:
                        report_mode = f" [상세 보고서 - 샘플 50개 - {model_name.upper()}]"
                    else:
                        report_mode = f" [{model_name.upper()}]"
                    
                    st.session_state.report_content += f"\n\n{'='*80}\n"
                    st.session_state.report_content += f"[{timestamp}]{report_mode} 질문: {user_question}\n"
                    st.session_state.report_content += f"{'='*80}\n\n"
                    st.session_state.report_content += response
        
        # 대화 히스토리 표시
        st.markdown("### 💬 대화 기록")
        
        if st.session_state.chat_history:
            for idx in range(0, len(st.session_state.chat_history), 2):
                if idx + 1 < len(st.session_state.chat_history):
                    # 질문
                    user_msg = st.session_state.chat_history[idx]
                    st.markdown(f"**👤 질문:**")
                    st.info(user_msg['content'])
                    
                    # 답변
                    ai_msg = st.session_state.chat_history[idx + 1]
                    st.markdown(f"**🤖 AI 분석:**")
                    st.success(ai_msg['content'])
                    
                    st.markdown("---")
            
            # 대화 초기화 버튼
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🗑️ 대화 기록 초기화", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                # 보고서 다운로드
                if st.session_state.report_content:
                    report_filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    
                    # 전체 보고서 생성
                    full_report = f"""
{'='*80}
YouTube 영상 데이터 분석 보고서
생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

# 데이터 개요
- 총 영상: {len(filtered_videos)}개
- 자막/STT: {len([v for v in filtered_videos if v.get('has_text')])}개
- 채널 수: {len(set(v['channel_id'] for v in filtered_videos))}개

{st.session_state.report_content}

{'='*80}
보고서 끝
{'='*80}
"""
                    
                    st.download_button(
                        label="📥 보고서 다운로드 (.txt)",
                        data=full_report,
                        file_name=report_filename,
                        mime="text/plain",
                        use_container_width=True,
                        key="download_report"
                    )
        else:
            st.info("💡 위에서 질문을 입력하고 '분석 요청' 버튼을 눌러보세요!")
            
            st.markdown("""
            **💬 일반 질문 예시:**
            - "조회수가 가장 높은 채널과 그 이유는?"
            - "스마트폰 케이스에 대한 언급이 많은 영상은?"
            - "배터리 관련 부정적 의견이 있나요?"
            - "각 채널의 타겟 오디언스 특징은?"
            
            **📄 상세 보고서 질문 예시 (체크박스 활성화 필요):**
            - "스마트폰 관련 콘텐츠를 토픽별로 분류하고 각 토픽마다 실제 언급 예시를 최소 10개씩 제시해주세요"
            - "iPhone과 Android 중 어떤 것이 더 많이 언급되나요? 각각의 언급 사례를 채널별로 정리해주세요"
            - "배터리, 충전, 케이스 등 액세서리 관련 토픽을 세부 분류하고 각 토픽의 실제 사용 예시를 보여주세요"
            - "카메라/촬영 관련 언급을 분석하고 채널별 특징과 구체적인 내용을 정리해주세요"
            
            **⚡ 데이터 범위 옵션:**
            - **샘플 50개**: 대표적인 패턴 파악, 빠르고 저렴
            - **전체 데이터**: 모든 영상 분석, 완전한 보고서
            
            **🤖 모델 비교:**
            - **GPT-4o-mini**: 16배 저렴, 2-3배 빠름, 일반 분석에 충분
            - **GPT-4o**: 최고 품질, 복잡한 분석 및 상세 보고서에 권장
            
            **📊 상세 보고서 모드 특징:**
            - 실제 영상의 전체 텍스트 데이터 포함
            - 채널명, 영상 제목, 조회수 등 상세 정보 제공
            - real_smartphone_topics.txt 수준의 체계적인 분석
            - 더 긴 응답 (최대 4000 토큰)
            """)
            
            st.info("💡 **추천**: GPT-4o-mini로 빠르게 테스트 후, 중요한 보고서는 GPT-4o + 전체 데이터로!")

if __name__ == "__main__":
    main()

