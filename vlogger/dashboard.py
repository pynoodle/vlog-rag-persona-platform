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

# 페이지 설정
st.set_page_config(
    page_title="YouTube 영상 데이터 분석 대시보드",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링 - 다크모드 대응
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF0000;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* 모든 텍스트 요소에 대해 명시적 색상 지정 */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] div,
    .stMarkdown p,
    .stMarkdown span,
    .stMarkdown div {
        color: #1f1f1f !important;
    }
    
    /* 다크 테마인 경우 흰색으로 */
    @media (prefers-color-scheme: dark) {
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] div,
        .stMarkdown p,
        .stMarkdown span,
        .stMarkdown div {
            color: #ffffff !important;
        }
    }
    
    /* 메트릭 카드 */
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: #1f1f1f !important;
    }
    
    /* 헤더 색상 */
    h1, h2, h3, h4, h5, h6 {
        color: #1f1f1f !important;
    }
    
    @media (prefers-color-scheme: dark) {
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all_videos(data_dir='youtube_data'):
    """모든 영상 데이터를 로드"""
    videos = []
    
    if not os.path.exists(data_dir):
        return videos
    
    channel_dirs = [d for d in os.listdir(data_dir) 
                   if os.path.isdir(os.path.join(data_dir, d))]
    
    for channel_id in channel_dirs:
        channel_path = os.path.join(data_dir, channel_id)
        
        # 채널 정보
        channel_info_path = os.path.join(channel_path, 'channel_info.json')
        channel_name = channel_id
        
        if os.path.exists(channel_info_path):
            try:
                with open(channel_info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    channel_name = info.get('channel_title', channel_id)
            except:
                pass
        
        # 영상 데이터
        json_files = glob.glob(os.path.join(channel_path, '*.json'))
        
        for json_file in json_files:
            if 'channel_info.json' in json_file:
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    video_data = json.load(f)
                
                video_data['channel_name'] = channel_name
                video_data['channel_id'] = channel_id
                
                # 전체 텍스트
                full_text = ""
                if video_data.get('transcript'):
                    full_text = " ".join([seg.get('text', '') for seg in video_data['transcript']])
                
                video_data['full_text'] = full_text
                video_data['has_transcript'] = len(full_text) > 0
                
                videos.append(video_data)
                
            except:
                continue
    
    return videos

def search_videos(videos, keyword):
    """키워드로 영상 검색"""
    keyword_lower = keyword.lower()
    results = []
    
    for video in videos:
        if not video.get('has_transcript'):
            continue
        
        if keyword_lower in video['full_text'].lower():
            # 매칭 세그먼트 찾기
            matching_segments = []
            for seg in video.get('transcript', []):
                if keyword_lower in seg.get('text', '').lower():
                    matching_segments.append(seg)
            
            results.append({
                **video,
                'match_count': len(matching_segments),
                'matching_segments': matching_segments
            })
    
    return sorted(results, key=lambda x: x['match_count'], reverse=True)

def main():
    # 헤더
    st.markdown('<h1 class="main-header">📱 YouTube 영상 데이터 분석 대시보드</h1>', 
                unsafe_allow_html=True)
    
    # 데이터 로드
    with st.spinner('데이터 로딩 중...'):
        videos = load_all_videos()
    
    if not videos:
        st.error("❌ 데이터를 찾을 수 없습니다. youtube_data 폴더를 확인하세요.")
        return
    
    # 기본 통계
    videos_with_transcript = [v for v in videos if v.get('has_transcript')]
    total_channels = len(set(v['channel_id'] for v in videos))
    
    # 사이드바 - 필터
    st.sidebar.header("🔍 필터")
    
    # 채널 선택
    all_channels = sorted(list(set(v['channel_name'] for v in videos)))
    selected_channels = st.sidebar.multiselect(
        "채널 선택",
        options=all_channels,
        default=[]
    )
    
    # 자막 유무 필터
    transcript_filter = st.sidebar.radio(
        "자막/STT 필터",
        options=["전체", "자막/STT 있음", "메타데이터만"],
        index=0
    )
    
    # 필터 적용
    filtered_videos = videos.copy()
    
    if selected_channels:
        filtered_videos = [v for v in filtered_videos if v['channel_name'] in selected_channels]
    
    if transcript_filter == "자막/STT 있음":
        filtered_videos = [v for v in filtered_videos if v.get('has_transcript')]
    elif transcript_filter == "메타데이터만":
        filtered_videos = [v for v in filtered_videos if not v.get('has_transcript')]
    
    # 탭 구성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 전체 통계", 
        "🔍 키워드 검색", 
        "📱 스마트폰 분석",
        "📺 채널 분석",
        "🔥 인기 영상"
    ])
    
    # ===== 탭 1: 전체 통계 =====
    with tab1:
        st.header("📊 전체 통계")
        
        # 주요 메트릭
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 영상 수", f"{len(filtered_videos):,}개")
        
        with col2:
            st.metric("채널 수", f"{len(set(v['channel_id'] for v in filtered_videos))}개")
        
        with col3:
            transcript_count = len([v for v in filtered_videos if v.get('has_transcript')])
            st.metric("자막/STT 있음", f"{transcript_count:,}개")
        
        with col4:
            transcript_rate = (transcript_count / len(filtered_videos) * 100) if filtered_videos else 0
            st.metric("자막 수집률", f"{transcript_rate:.1f}%")
        
        st.markdown("---")
        
        # 채널별 영상 수 차트
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📺 채널별 영상 수")
            
            channel_counts = Counter(v['channel_name'] for v in filtered_videos)
            df_channels = pd.DataFrame(
                channel_counts.most_common(15),
                columns=['채널', '영상 수']
            )
            
            fig = px.bar(df_channels, x='영상 수', y='채널', orientation='h',
                        color='영상 수', color_continuous_scale='Reds')
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📝 자막/STT 타입 분포")
            
            transcript_types = Counter(v.get('transcript_type', 'none') 
                                      for v in filtered_videos)
            
            df_types = pd.DataFrame(
                transcript_types.items(),
                columns=['타입', '개수']
            )
            
            type_labels = {
                'subtitle': '📄 수동 자막',
                'auto-generated': '🤖 자동 생성',
                'whisper-stt': '🎙️ Whisper STT',
                'none': '❌ 없음',
                None: '❌ 없음'
            }
            df_types['타입'] = df_types['타입'].map(lambda x: type_labels.get(x, x))
            
            fig = px.pie(df_types, values='개수', names='타입',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # 조회수 분포
        st.subheader("👁️ 조회수 분포")
        
        view_counts = []
        for v in filtered_videos:
            try:
                view_counts.append(int(v['metadata'].get('view_count', 0)))
            except:
                pass
        
        if view_counts:
            df_views = pd.DataFrame({'조회수': view_counts})
            
            fig = px.histogram(df_views, x='조회수', nbins=50,
                             labels={'조회수': '조회수', 'count': '영상 수'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("평균 조회수", f"{sum(view_counts)/len(view_counts):,.0f}")
            with col2:
                st.metric("최대 조회수", f"{max(view_counts):,}")
            with col3:
                st.metric("중앙값", f"{sorted(view_counts)[len(view_counts)//2]:,}")
    
    # ===== 탭 2: 키워드 검색 =====
    with tab2:
        st.header("🔍 키워드 검색")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_keyword = st.text_input(
                "검색 키워드 입력",
                placeholder="예: 아이폰, battery, 케이스"
            )
        
        with col2:
            st.write("")
            st.write("")
            search_button = st.button("🔍 검색", type="primary")
        
        if search_keyword or search_button:
            if search_keyword:
                with st.spinner(f"'{search_keyword}' 검색 중..."):
                    results = search_videos(videos_with_transcript, search_keyword)
                
                if results:
                    st.success(f"✅ {len(results)}개 영상에서 총 {sum(r['match_count'] for r in results)}회 발견!")
                    
                    # 검색 결과 표시
                    for idx, result in enumerate(results[:20], 1):
                        with st.expander(f"{idx}. {result['metadata']['title']} ({result['match_count']}회 언급)"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**채널:** {result['channel_name']}")
                                st.write(f"**URL:** {result['metadata']['video_url']}")
                                
                                try:
                                    view_count = int(result['metadata']['view_count'])
                                    st.write(f"**조회수:** {view_count:,}")
                                except:
                                    st.write(f"**조회수:** {result['metadata']['view_count']}")
                            
                            with col2:
                                st.metric("언급 횟수", f"{result['match_count']}회")
                            
                            # 매칭 세그먼트 표시
                            st.markdown("**언급 내용:**")
                            for seg in result['matching_segments'][:3]:
                                timestamp = seg.get('start', 0)
                                minutes = int(timestamp // 60)
                                seconds = int(timestamp % 60)
                                text = seg.get('text', '')
                                
                                st.markdown(f"⏱️ `[{minutes:02d}:{seconds:02d}]` {text}")
                            
                            if len(result['matching_segments']) > 3:
                                st.info(f"... 외 {len(result['matching_segments']) - 3}개 언급")
                    
                    if len(results) > 20:
                        st.info(f"... 외 {len(results) - 20}개 영상 (상위 20개만 표시)")
                else:
                    st.warning(f"'{search_keyword}'가 포함된 영상을 찾을 수 없습니다.")
    
    # ===== 탭 3: 스마트폰 분석 =====
    with tab3:
        st.header("📱 스마트폰 관련 콘텐츠 분석")
        
        # 스마트폰 관련 키워드
        smartphone_keywords = ['smartphone', 'iphone', 'galaxy', 'android', 'phone',
                              'imessage', 'facetime', '스마트폰', '아이폰', '갤럭시', '핸드폰']
        
        # 스마트폰 관련 영상 필터링
        smartphone_videos = []
        for video in videos_with_transcript:
            if any(kw.lower() in video['full_text'].lower() for kw in smartphone_keywords):
                smartphone_videos.append(video)
        
        st.metric("스마트폰 관련 영상", f"{len(smartphone_videos)}개 / {len(videos_with_transcript)}개")
        
        if smartphone_videos:
            # 토픽 분석
            st.subheader("📊 주요 토픽 분포")
            
            topics = {
                '🎨 폰 케이스/액세서리': ['case', 'accessories', 'airpods', 'screen protector', '케이스'],
                '🔋 배터리/충전': ['battery', 'charging', 'charger', '배터리', '충전'],
                '📸 촬영/카메라': ['camera', 'selfie', 'photo', 'filming', '카메라', '셀카'],
                '📲 앱/소프트웨어': ['app', 'ios', 'android', 'widget', '앱'],
                '📱 디지털 웰빙': ['screen time', 'addiction', 'notification', '스크린타임'],
                '📦 신제품/언박싱': ['unboxing', 'iphone 16', 'iphone 15', 'new phone', '언박싱'],
                '💬 메시징': ['imessage', 'facetime', 'whatsapp', 'text', '메시지'],
            }
            
            topic_counts = {}
            for topic_name, keywords in topics.items():
                count = 0
                for video in smartphone_videos:
                    if any(kw.lower() in video['full_text'].lower() for kw in keywords):
                        count += 1
                topic_counts[topic_name] = count
            
            # 차트
            df_topics = pd.DataFrame(
                sorted(topic_counts.items(), key=lambda x: x[1], reverse=True),
                columns=['토픽', '영상 수']
            )
            
            fig = px.bar(df_topics, x='영상 수', y='토픽', orientation='h',
                        color='영상 수', color_continuous_scale='Viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # 채널별 스마트폰 관련 영상 수
            st.subheader("📺 채널별 스마트폰 콘텐츠")
            
            channel_smartphone = Counter(v['channel_name'] for v in smartphone_videos)
            df_channel_phone = pd.DataFrame(
                channel_smartphone.most_common(10),
                columns=['채널', '스마트폰 관련 영상']
            )
            
            fig = px.bar(df_channel_phone, x='스마트폰 관련 영상', y='채널',
                        orientation='h', color='스마트폰 관련 영상',
                        color_continuous_scale='Oranges')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # ===== 탭 4: 채널 분석 =====
    with tab4:
        st.header("📺 채널별 분석")
        
        # 채널 선택
        channel_to_analyze = st.selectbox(
            "분석할 채널 선택",
            options=sorted(list(set(v['channel_name'] for v in filtered_videos)))
        )
        
        if channel_to_analyze:
            channel_videos = [v for v in filtered_videos if v['channel_name'] == channel_to_analyze]
            channel_with_text = [v for v in channel_videos if v.get('has_transcript')]
            
            # 채널 통계
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 영상", f"{len(channel_videos)}개")
            
            with col2:
                st.metric("자막/STT", f"{len(channel_with_text)}개")
            
            with col3:
                total_views = sum(int(v['metadata'].get('view_count', 0)) 
                                for v in channel_videos 
                                if v['metadata'].get('view_count'))
                st.metric("총 조회수", f"{total_views:,}")
            
            with col4:
                avg_views = total_views / len(channel_videos) if channel_videos else 0
                st.metric("평균 조회수", f"{avg_views:,.0f}")
            
            st.markdown("---")
            
            # 영상 목록
            st.subheader("🎬 영상 목록")
            
            # 정렬 옵션
            sort_by = st.radio(
                "정렬",
                options=["조회수 높은 순", "조회수 낮은 순", "최신순"],
                horizontal=True
            )
            
            sorted_videos = channel_videos.copy()
            
            if sort_by == "조회수 높은 순":
                sorted_videos.sort(key=lambda x: int(x['metadata'].get('view_count', 0)), reverse=True)
            elif sort_by == "조회수 낮은 순":
                sorted_videos.sort(key=lambda x: int(x['metadata'].get('view_count', 0)))
            
            for idx, video in enumerate(sorted_videos[:20], 1):
                metadata = video['metadata']
                video_id = metadata.get('video_id', f'video_{idx}')
                
                with st.expander(f"{idx}. {metadata['title']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**URL:** {metadata['video_url']}")
                        st.write(f"**게시일:** {metadata.get('published_at', 'N/A')}")
                        
                        try:
                            view_count = int(metadata['view_count'])
                            st.write(f"**조회수:** {view_count:,}")
                        except:
                            st.write(f"**조회수:** {metadata['view_count']}")
                        
                        st.write(f"**좋아요:** {metadata.get('like_count', 0)}")
                        st.write(f"**댓글:** {metadata.get('comment_count', 0)}")
                    
                    with col2:
                        has_text = "✅ 있음" if video.get('has_transcript') else "❌ 없음"
                        st.metric("자막/STT", has_text)
                        
                        trans_type = video.get('transcript_type', 'none')
                        type_emoji = {
                            'subtitle': '📄',
                            'auto-generated': '🤖',
                            'whisper-stt': '🎙️',
                            'none': '❌'
                        }
                        st.write(f"{type_emoji.get(trans_type, '❓')} {trans_type}")
                    
                    # 설명 (고유 key 사용)
                    if metadata.get('description'):
                        st.markdown("**📝 설명:**")
                        st.text(metadata['description'][:500])
    
    # ===== 탭 5: 인기 영상 =====
    with tab5:
        st.header("🔥 인기 영상 Top 20")
        
        # 필터 옵션
        popularity_filter = st.radio(
            "필터",
            options=["전체", "스마트폰 관련만"],
            horizontal=True
        )
        
        videos_to_rank = filtered_videos.copy()
        
        if popularity_filter == "스마트폰 관련만":
            smartphone_keywords = ['smartphone', 'iphone', 'galaxy', 'android', 'phone',
                                  '스마트폰', '아이폰', '갤럭시', '핸드폰']
            videos_to_rank = [v for v in videos_to_rank 
                            if v.get('has_transcript') and 
                            any(kw.lower() in v['full_text'].lower() for kw in smartphone_keywords)]
        
        # 조회수로 정렬
        videos_to_rank.sort(key=lambda x: int(x['metadata'].get('view_count', 0)), reverse=True)
        
        for idx, video in enumerate(videos_to_rank[:20], 1):
            metadata = video['metadata']
            
            with st.container():
                col1, col2, col3 = st.columns([1, 5, 2])
                
                with col1:
                    st.markdown(f"### {idx}")
                
                with col2:
                    st.markdown(f"**{metadata['title']}**")
                    st.caption(f"📺 {video['channel_name']}")
                
                with col3:
                    try:
                        view_count = int(metadata['view_count'])
                        st.metric("조회수", f"{view_count:,}")
                    except:
                        st.metric("조회수", metadata['view_count'])
                
                st.markdown(f"🔗 [{metadata['video_url']}]({metadata['video_url']})")
                st.markdown("---")
    
    # 사이드바 - 통계 요약
    st.sidebar.markdown("---")
    st.sidebar.header("📊 현재 필터 통계")
    st.sidebar.metric("영상 수", f"{len(filtered_videos)}개")
    st.sidebar.metric("자막/STT", f"{len([v for v in filtered_videos if v.get('has_transcript')])}개")
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.caption("📅 마지막 업데이트: " + datetime.now().strftime('%Y-%m-%d %H:%M'))
    st.sidebar.caption("💻 YouTube 영상 데이터 분석 시스템")

if __name__ == "__main__":
    main()

