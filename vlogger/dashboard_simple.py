# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import glob
from collections import Counter

# 페이지 설정
st.set_page_config(
    page_title="YouTube 영상 데이터 분석",
    page_icon="📱",
    layout="wide"
)

@st.cache_data
def load_data():
    """데이터 로드"""
    videos = []
    data_dir = 'youtube_data'
    
    if not os.path.exists(data_dir):
        return videos
    
    for channel_dir in os.listdir(data_dir):
        channel_path = os.path.join(data_dir, channel_dir)
        if not os.path.isdir(channel_path):
            continue
        
        # 채널 정보
        channel_info = os.path.join(channel_path, 'channel_info.json')
        channel_name = channel_dir
        
        if os.path.exists(channel_info):
            try:
                with open(channel_info, 'r', encoding='utf-8') as f:
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
                
                video['channel_name'] = channel_name
                
                # 전체 텍스트 생성
                full_text = ""
                if video.get('transcript'):
                    full_text = " ".join([s.get('text', '') for s in video['transcript']])
                
                video['full_text'] = full_text
                videos.append(video)
            except:
                continue
    
    return videos

# 메인
st.title("📱 YouTube 영상 데이터 분석 대시보드")

# 데이터 로드
videos = load_data()

if not videos:
    st.error("데이터를 찾을 수 없습니다.")
    st.stop()

videos_with_text = [v for v in videos if v.get('full_text')]

# 탭
tab1, tab2, tab3, tab4 = st.tabs(["📊 통계", "🔍 검색", "📺 채널", "🔥 인기"])

# 탭 1: 통계
with tab1:
    st.header("📊 전체 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 영상", f"{len(videos):,}")
    col2.metric("채널 수", f"{len(set(v['channel_name'] for v in videos))}")
    col3.metric("자막/STT", f"{len(videos_with_text):,}")
    
    rate = len(videos_with_text) / len(videos) * 100 if videos else 0
    col4.metric("수집률", f"{rate:.1f}%")
    
    st.markdown("---")
    
    # 채널별 영상 수
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("채널별 영상 수 (Top 15)")
        channel_counts = Counter(v['channel_name'] for v in videos)
        df = pd.DataFrame(channel_counts.most_common(15), columns=['채널', '영상수'])
        
        fig = px.bar(df, x='영상수', y='채널', orientation='h')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("자막 타입 분포")
        types = Counter(v.get('transcript_type', 'none') for v in videos)
        df_types = pd.DataFrame(types.items(), columns=['타입', '개수'])
        
        type_map = {
            'subtitle': '📄 수동자막',
            'auto-generated': '🤖 자동생성',
            'whisper-stt': '🎙️ Whisper',
            'none': '❌ 없음',
            None: '❌ 없음'
        }
        df_types['타입'] = df_types['타입'].map(lambda x: type_map.get(x, x))
        
        fig = px.pie(df_types, values='개수', names='타입')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# 탭 2: 검색
with tab2:
    st.header("🔍 키워드 검색")
    
    keyword = st.text_input("검색어를 입력하세요", placeholder="예: 아이폰, battery, 케이스")
    
    if keyword:
        st.info(f"🔍 '{keyword}' 검색 중...")
        
        results = []
        for video in videos_with_text:
            if keyword.lower() in video['full_text'].lower():
                count = video['full_text'].lower().count(keyword.lower())
                results.append({
                    'channel': video['channel_name'],
                    'title': video['metadata']['title'],
                    'url': video['metadata']['video_url'],
                    'views': int(video['metadata'].get('view_count', 0)),
                    'count': count,
                    'video': video
                })
        
        results.sort(key=lambda x: x['count'], reverse=True)
        
        if results:
            st.success(f"✅ {len(results)}개 영상에서 총 {sum(r['count'] for r in results)}회 발견!")
            
            for idx, r in enumerate(results[:15], 1):
                st.markdown(f"### {idx}. {r['title']}")
                st.write(f"**채널:** {r['channel']} | **언급:** {r['count']}회 | **조회수:** {r['views']:,}")
                st.write(f"**URL:** {r['url']}")
                
                # 예시 세그먼트
                for seg in r['video']['transcript']:
                    if keyword.lower() in seg.get('text', '').lower():
                        ts = seg.get('start', 0)
                        m, s = int(ts // 60), int(ts % 60)
                        st.caption(f"[{m:02d}:{s:02d}] {seg.get('text', '')[:150]}")
                        break
                
                st.markdown("---")
        else:
            st.warning(f"'{keyword}'를 찾을 수 없습니다.")

# 탭 3: 채널
with tab3:
    st.header("📺 채널별 분석")
    
    channels = sorted(list(set(v['channel_name'] for v in videos)))
    selected = st.selectbox("채널 선택", channels)
    
    if selected:
        ch_videos = [v for v in videos if v['channel_name'] == selected]
        ch_with_text = [v for v in ch_videos if v.get('full_text')]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("총 영상", f"{len(ch_videos)}")
        col2.metric("자막/STT", f"{len(ch_with_text)}")
        
        total_views = sum(int(v['metadata'].get('view_count', 0)) for v in ch_videos)
        col3.metric("총 조회수", f"{total_views:,}")
        
        st.markdown("---")
        st.subheader("영상 목록")
        
        for idx, v in enumerate(sorted(ch_videos, 
                                       key=lambda x: int(x['metadata'].get('view_count', 0)),
                                       reverse=True)[:20], 1):
            meta = v['metadata']
            st.write(f"**{idx}. {meta['title']}**")
            st.write(f"조회수: {int(meta.get('view_count', 0)):,} | 자막: {'✅' if v.get('full_text') else '❌'}")
            st.caption(meta['video_url'])
            st.markdown("---")

# 탭 4: 인기 영상
with tab4:
    st.header("🔥 인기 영상 Top 20")
    
    filter_opt = st.radio("필터", ["전체", "스마트폰 관련"], horizontal=True)
    
    to_rank = videos.copy()
    
    if filter_opt == "스마트폰 관련":
        keywords = ['iphone', 'phone', 'smartphone', 'galaxy', 'android',
                   '아이폰', '폰', '스마트폰', '갤럭시']
        to_rank = [v for v in videos_with_text 
                   if any(k.lower() in v['full_text'].lower() for k in keywords)]
    
    to_rank.sort(key=lambda x: int(x['metadata'].get('view_count', 0)), reverse=True)
    
    for idx, v in enumerate(to_rank[:20], 1):
        meta = v['metadata']
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### {idx}. {meta['title']}")
            st.write(f"**채널:** {v['channel_name']}")
            st.caption(meta['video_url'])
        
        with col2:
            views = int(meta.get('view_count', 0))
            st.metric("조회수", f"{views:,}")
        
        st.markdown("---")

# 사이드바
st.sidebar.header("📊 현재 상태")
st.sidebar.metric("영상", f"{len(videos)}")
st.sidebar.metric("자막/STT", f"{len(videos_with_text)}")
st.sidebar.metric("채널", f"{len(set(v['channel_name'] for v in videos))}")

