# -*- coding: utf-8 -*-
import streamlit as st
import time
import json
from datetime import datetime
from cluster_chatbots import ChatbotManager
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random

class EnhancedPersonaGUI:
    def __init__(self):
        self.manager = ChatbotManager()
        self.current_chatbot = None
        
        # 페르소나 정보 (더 상세한 정보 포함)
        self.personas = {
            0: {
                'name': 'Emma',
                'avatar': '👩‍🍳',
                'color': '#FF6B6B',
                'description': '다재다능한 라이프스타일 인플루언서',
                'specialty': '요리, 패션, 예술, 뷰티, 여행',
                'catchphrase': 'OMG, this is so cute!',
                'age': '22세',
                'personality': ['창의적', '다재다능', '트렌드 민감', '에너지틱', '감성적'],
                'interests': ['요리', '패션', '예술', '뷰티', '여행'],
                'target_audience': '다양한 관심사를 가진 Gen Z'
            },
            1: {
                'name': 'Victoria',
                'avatar': '🏠',
                'color': '#4ECDC4',
                'description': '홈 & 뷰티 중심 라이프스타일 인플루언서',
                'specialty': '홈 데코, 일상 공유, 반려동물 케어',
                'catchphrase': 'Let me show you my cozy life!',
                'age': '24세',
                'personality': ['실용적', '감성적', '홈 데코 전문', '일상 공유', '친근함'],
                'interests': ['홈 데코', '요리', '일상 공유', '반려동물', '테크'],
                'target_audience': '홈 라이프에 관심 있는 Gen Z'
            },
            2: {
                'name': 'Misha',
                'avatar': '📚',
                'color': '#45B7D1',
                'description': '활발한 콘텐츠 크리에이터',
                'specialty': '독서, 저널링, 자기계발, 테크',
                'catchphrase': 'Let\'s make today amazing!',
                'age': '23세',
                'personality': ['에너지틱', '창의적', '자기계발', '활동적', '다양함'],
                'interests': ['독서', '저널링', '테크', '요리', '홈 데코'],
                'target_audience': '자기계발에 관심 있는 Gen Z'
            },
            3: {
                'name': 'Philip',
                'avatar': '📸',
                'color': '#96CEB4',
                'description': '예술 & 크래프트 전문가',
                'specialty': '사진, 예술, 크래프트, 요리',
                'catchphrase': 'Art is everywhere',
                'age': '25세',
                'personality': ['예술적', '창의적', '디테일 지향', '독창적', '감성적'],
                'interests': ['사진', '예술', '요리', '테크', '크래프트'],
                'target_audience': '창의적 활동에 관심 있는 Gen Z'
            },
            4: {
                'name': 'James',
                'avatar': '💄',
                'color': '#FFEAA7',
                'description': '뷰티 & 패션 전문가',
                'specialty': '뷰티, 패션, 스타일링',
                'catchphrase': 'Beauty is power',
                'age': '26세',
                'personality': ['전문적', '트렌드 민감', '스타일리시', '뷰티 전문', '패션 전문'],
                'interests': ['뷰티', '패션', '요리', '예술', '테크'],
                'target_audience': '뷰티와 패션에 관심 있는 Gen Z'
            }
        }
    
    def setup_page_config(self):
        """페이지 설정"""
        st.set_page_config(
            page_title="Gen Z 인플루언서 페르소나봇",
            page_icon="🎭",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def setup_css(self):
        """CSS 스타일 설정"""
        st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        .persona-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            margin: 0.5rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .persona-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .persona-card.selected {
            border: 3px solid #FFD700;
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.6);
            transform: scale(1.02);
        }
        
        .chat-message {
            padding: 1rem 1.5rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            max-width: 85%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .bot-message {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            margin-right: auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .avatar-large {
            font-size: 4rem;
            text-align: center;
            margin: 1rem 0;
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {
                transform: translateY(0);
            }
            40% {
                transform: translateY(-10px);
            }
            60% {
                transform: translateY(-5px);
            }
        }
        
        .trend-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 5px solid #667eea;
        }
        
        .lifestyle-tip {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .content-idea {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .stats-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .feature-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .typing-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: #667eea;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        @keyframes typing {
            0%, 80%, 100% {
                transform: scale(0);
            }
            40% {
                transform: scale(1);
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def show_sidebar(self):
        """사이드바 표시"""
        with st.sidebar:
            st.markdown("""
            <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 1rem;'>
                <h2>🎭 페르소나 선택</h2>
                <p>원하는 인플루언서를 선택하세요!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 페르소나 선택
            for cluster_id, persona in self.personas.items():
                if st.button(f"{persona['avatar']} **{persona['name']}**", key=f"persona_{cluster_id}", use_container_width=True):
                    st.session_state.selected_persona = cluster_id
                    st.rerun()
            
            st.markdown("---")
            
            # 현재 선택된 페르소나 정보
            if 'selected_persona' in st.session_state:
                persona = self.personas[st.session_state.selected_persona]
                chatbot = self.manager.select_chatbot(st.session_state.selected_persona)
                stats = chatbot.get_knowledge_stats()
                
                st.markdown(f"""
                <div class='persona-card selected'>
                    <h3>{persona['avatar']} {persona['name']}</h3>
                    <p><strong>나이:</strong> {persona['age']}</p>
                    <p><strong>전문분야:</strong> {persona['specialty']}</p>
                    <p><strong>특징:</strong> {persona['description']}</p>
                    <p><strong>대표 문구:</strong> "{persona['catchphrase']}"</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 지식베이스 통계
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📊 전사본", f"{stats['total_transcripts']}개")
                with col2:
                    st.metric("🔑 키워드", f"{len(stats['top_keywords'])}개")
                
                # 상위 키워드 표시
                if stats['top_keywords']:
                    st.markdown("### 🔥 상위 키워드")
                    keywords = list(stats['top_keywords'].keys())[:5]
                    for keyword in keywords:
                        st.markdown(f"• {keyword}")
    
    def show_chat_interface(self):
        """채팅 인터페이스 표시"""
        st.title("💬 페르소나와 대화하기")
        
        if 'selected_persona' not in st.session_state:
            st.warning("👈 사이드바에서 페르소나를 선택해주세요!")
            return
        
        # 현재 페르소나 정보
        persona = self.personas[st.session_state.selected_persona]
        chatbot = self.manager.select_chatbot(st.session_state.selected_persona)
        
        # 페르소나 소개
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"<div class='avatar-large'>{persona['avatar']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='persona-card'>
                <h2>{persona['name']} ({persona['age']})</h2>
                <p><strong>전문분야:</strong> {persona['specialty']}</p>
                <p><strong>특징:</strong> {persona['description']}</p>
                <p><strong>대표 문구:</strong> "{persona['catchphrase']}"</p>
                <p><strong>타겟:</strong> {persona['target_audience']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 채팅 기록 표시
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # 채팅 기록 컨테이너
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class='chat-message user-message'>
                        <strong>👤 당신:</strong> {message['content']}
                        <br><small style='opacity: 0.7;'>{message.get('timestamp', '')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='chat-message bot-message'>
                        <strong>🤖 {persona['name']}:</strong> {message['content']}
                        <br><small style='opacity: 0.7;'>{message.get('timestamp', '')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 메시지 입력
        st.markdown("---")
        
        # 빠른 질문 버튼들
        st.markdown("### 💡 빠른 질문")
        quick_questions = {
            0: ["오늘 뭐 해?", "요리 레시피 추천해줘!", "패션 트렌드 알려줘!"],
            1: ["홈 데코 팁 알려줘!", "아늑한 집 만들기", "반려동물 케어 팁"],
            2: ["독서 추천해줘!", "저널링 어떻게 해?", "자기계발 팁"],
            3: ["예쁜 사진 찍는 방법", "예술 활동 추천", "창의적 요리"],
            4: ["뷰티 트렌드 알려줘!", "스킨케어 루틴", "패션 스타일링"]
        }
        
        questions = quick_questions.get(st.session_state.selected_persona, ["안녕!"])
        cols = st.columns(len(questions))
        for i, question in enumerate(questions):
            with cols[i]:
                if st.button(f"💬 {question}", use_container_width=True):
                    self.send_message(question, chatbot, persona)
                    st.rerun()
        
        # 메시지 입력
        user_input = st.text_input("메시지를 입력하세요:", key="user_input", placeholder="안녕! 오늘 뭐 해?")
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            if st.button("📤 전송", use_container_width=True):
                if user_input:
                    self.send_message(user_input, chatbot, persona)
                    st.rerun()
        
        with col2:
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col3:
            if st.button("💾 저장", use_container_width=True):
                self.save_chat_history(persona['name'])
                st.success("대화 기록이 저장되었습니다!")
        
        with col4:
            if st.button("🎲 랜덤", use_container_width=True):
                random_question = random.choice(questions)
                self.send_message(random_question, chatbot, persona)
                st.rerun()
    
    def send_message(self, message, chatbot, persona):
        """메시지 전송 및 스트리밍 응답"""
        # 사용자 메시지 추가
        st.session_state.chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        # 봇 응답 생성 (스트리밍 효과)
        with st.spinner(f"{persona['name']}가 답변을 준비 중..."):
            response = chatbot.chat(message)
        
        # 봇 응답 추가
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    
    def show_trend_analysis(self):
        """트렌드 분석 탭"""
        st.title("📈 트렌드 분석")
        
        if 'selected_persona' not in st.session_state:
            st.warning("👈 사이드바에서 페르소나를 선택해주세요!")
            return
        
        persona = self.personas[st.session_state.selected_persona]
        chatbot = self.manager.select_chatbot(st.session_state.selected_persona)
        
        # 트렌드 분석 입력
        col1, col2 = st.columns([3, 1])
        with col1:
            trend_topic = st.text_input("분석하고 싶은 트렌드 주제를 입력하세요:", placeholder="뷰티, 패션, 요리, 홈데코, 자기계발 등")
        with col2:
            analyze_btn = st.button("🔍 분석", use_container_width=True)
        
        if analyze_btn and trend_topic:
            with st.spinner("트렌드 분석 중..."):
                analysis = chatbot.get_trend_analysis(trend_topic)
                
                st.markdown(f"""
                <div class='trend-card'>
                    <h3>📊 {trend_topic} 트렌드 분석</h3>
                    <p><strong>분석자:</strong> {persona['name']} ({persona['specialty']})</p>
                    <p><strong>분석 시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <hr>
                    <div style='white-space: pre-wrap; line-height: 1.6;'>{analysis}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 페르소나별 트렌드 인사이트
        st.markdown("### 🎯 페르소나별 특화 트렌드")
        
        trend_insights = {
            0: "요리, 패션, 예술, 뷰티, 여행 분야의 최신 트렌드와 인사이트",
            1: "홈 데코, 일상 공유, 반려동물 케어 관련 트렌드와 실용적 팁",
            2: "독서, 저널링, 자기계발, 테크 분야의 성장 트렌드",
            3: "사진, 예술, 크래프트, 창의적 활동의 예술적 트렌드",
            4: "뷰티, 패션, 스타일링 관련 전문 트렌드와 가이드"
        }
        
        st.info(f"💡 {persona['name']}의 전문분야: {trend_insights[st.session_state.selected_persona]}")
        
        # 트렌드 키워드 시각화
        if hasattr(chatbot, 'knowledge_base') and chatbot.knowledge_base.get('top_keywords'):
            keywords = list(chatbot.knowledge_base['top_keywords'].items())[:10]
            
            if keywords:
                df_keywords = pd.DataFrame(keywords, columns=['키워드', '빈도'])
                fig = px.bar(df_keywords, x='빈도', y='키워드', orientation='h', 
                           title=f"{persona['name']}의 주요 키워드 트렌드",
                           color='빈도',
                           color_continuous_scale='viridis')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # 트렌드 카테고리별 분석
        st.markdown("### 📊 카테고리별 트렌드 분석")
        
        trend_categories = {
            0: ["요리 트렌드", "패션 트렌드", "뷰티 트렌드", "여행 트렌드"],
            1: ["홈 데코 트렌드", "일상 루틴 트렌드", "반려동물 트렌드"],
            2: ["독서 트렌드", "자기계발 트렌드", "테크 트렌드"],
            3: ["사진 트렌드", "예술 트렌드", "크래프트 트렌드"],
            4: ["뷰티 트렌드", "패션 트렌드", "스타일링 트렌드"]
        }
        
        categories = trend_categories[st.session_state.selected_persona]
        
        cols = st.columns(2)
        for i, category in enumerate(categories):
            with cols[i % 2]:
                if st.button(f"📈 {category}", use_container_width=True):
                    with st.spinner(f"{category} 분석 중..."):
                        analysis = chatbot.get_trend_analysis(category)
                        
                        st.markdown(f"""
                        <div class='trend-card'>
                            <h4>📈 {category}</h4>
                            <div style='white-space: pre-wrap; line-height: 1.6;'>{analysis}</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    def show_lifestyle_guide(self):
        """라이프스타일 가이드 탭"""
        st.title("🏠 라이프스타일 가이드")
        
        if 'selected_persona' not in st.session_state:
            st.warning("👈 사이드바에서 페르소나를 선택해주세요!")
            return
        
        persona = self.personas[st.session_state.selected_persona]
        chatbot = self.manager.select_chatbot(st.session_state.selected_persona)
        
        # 라이프스타일 가이드 생성
        if st.button("💡 라이프스타일 팁 생성", use_container_width=True):
            with st.spinner(f"{persona['name']}의 라이프스타일 팁을 생성 중..."):
                tips = chatbot.get_lifestyle_tips()
                
                st.markdown(f"""
                <div class='lifestyle-tip'>
                    <h3>🌟 {persona['name']}의 라이프스타일 가이드</h3>
                    <p><strong>전문분야:</strong> {persona['specialty']}</p>
                    <hr>
                    <div style='white-space: pre-wrap; line-height: 1.6;'>{tips}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 페르소나별 특화 가이드
        st.markdown("### 🎯 전문분야별 가이드")
        
        guide_categories = {
            0: ["요리 초보자를 위한 레시피", "패션 스타일링 팁", "예술 활동 아이디어", "뷰티 루틴"],
            1: ["홈 데코 아이디어", "일상 루틴 만들기", "반려동물 케어", "아늑한 공간 만들기"],
            2: ["독서 방법", "저널링 기법", "자기계발 계획", "생산성 향상"],
            3: ["사진 촬영 기법", "예술 프로젝트", "창의적 요리", "DIY 크래프트"],
            4: ["뷰티 루틴", "패션 코디", "스타일링 팁", "메이크업 기법"]
        }
        
        categories = guide_categories[st.session_state.selected_persona]
        
        cols = st.columns(2)
        for i, category in enumerate(categories):
            with cols[i % 2]:
                if st.button(f"📋 {category}", use_container_width=True):
                    with st.spinner(f"{category} 가이드 생성 중..."):
                        guide = chatbot.chat(f"{category}에 대한 상세한 가이드를 알려주세요!")
                        
                        st.markdown(f"""
                        <div class='lifestyle-tip'>
                            <h4>📋 {category}</h4>
                            <div style='white-space: pre-wrap; line-height: 1.6;'>{guide}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # 라이프스타일 통계
        st.markdown("### 📊 라이프스타일 통계")
        
        if hasattr(chatbot, 'knowledge_base') and chatbot.knowledge_base.get('top_keywords'):
            keywords = list(chatbot.knowledge_base['top_keywords'].items())[:8]
            
            if keywords:
                df_keywords = pd.DataFrame(keywords, columns=['키워드', '빈도'])
                fig = px.pie(df_keywords, values='빈도', names='키워드', 
                           title=f"{persona['name']}의 라이프스타일 키워드 분포")
                st.plotly_chart(fig, use_container_width=True)
    
    def show_content_creation(self):
        """콘텐츠 제작 탭"""
        st.title("🎬 콘텐츠 제작")
        
        if 'selected_persona' not in st.session_state:
            st.warning("👈 사이드바에서 페르소나를 선택해주세요!")
            return
        
        persona = self.personas[st.session_state.selected_persona]
        chatbot = self.manager.select_chatbot(st.session_state.selected_persona)
        
        # 콘텐츠 아이디어 생성
        col1, col2 = st.columns([3, 1])
        with col1:
            content_topic = st.text_input("콘텐츠 주제를 입력하세요:", placeholder="요리, 패션, 뷰티, 홈데코, 자기계발 등")
        with col2:
            create_btn = st.button("💡 아이디어 생성", use_container_width=True)
        
        if create_btn and content_topic:
            with st.spinner("콘텐츠 아이디어 생성 중..."):
                idea = chatbot.chat(f"{content_topic}에 대한 인플루언서 스타일의 콘텐츠 아이디어를 알려주세요!")
                
                st.markdown(f"""
                <div class='content-idea'>
                    <h3>🎬 {content_topic} 콘텐츠 아이디어</h3>
                    <p><strong>제작자:</strong> {persona['name']} 스타일</p>
                    <p><strong>전문분야:</strong> {persona['specialty']}</p>
                    <hr>
                    <div style='white-space: pre-wrap; line-height: 1.6;'>{idea}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 페르소나별 콘텐츠 스타일
        st.markdown("### 🎭 콘텐츠 스타일 가이드")
        
        content_styles = {
            0: "다양한 라이프스타일을 다루는 올라운드 콘텐츠",
            1: "홈 라이프와 일상 공유 중심의 아늑한 콘텐츠",
            2: "자기계발과 성장을 다루는 에너지틱한 콘텐츠",
            3: "예술과 창의성을 강조하는 세련된 콘텐츠",
            4: "뷰티와 패션에 특화된 전문적인 콘텐츠"
        }
        
        st.info(f"💡 {persona['name']}의 콘텐츠 스타일: {content_styles[st.session_state.selected_persona]}")
        
        # 콘텐츠 유형별 아이디어
        st.markdown("### 🎬 콘텐츠 유형별 아이디어")
        
        content_types = {
            0: ["요리 레시피", "패션 스타일링", "여행 브이로그", "예술 DIY", "뷰티 튜토리얼"],
            1: ["홈 데코 투어", "일상 루틴", "반려동물 케어", "아늑한 라이프", "홈 쿠킹"],
            2: ["독서 리뷰", "저널링 방법", "자기계발 팁", "테크 리뷰", "생산성 팁"],
            3: ["사진 촬영", "예술 프로젝트", "크래프트 DIY", "창의적 요리", "아트 튜토리얼"],
            4: ["뷰티 튜토리얼", "패션 코디", "스타일링 팁", "메이크업 리뷰", "뷰티 루틴"]
        }
        
        types = content_types[st.session_state.selected_persona]
        
        cols = st.columns(3)
        for i, content_type in enumerate(types):
            with cols[i % 3]:
                if st.button(f"🎬 {content_type}", use_container_width=True):
                    with st.spinner(f"{content_type} 콘텐츠 아이디어 생성 중..."):
                        idea = chatbot.chat(f"{content_type}에 대한 인플루언서 콘텐츠 아이디어를 구체적으로 알려주세요!")
                        
                        st.markdown(f"""
                        <div class='content-idea'>
                            <h4>🎬 {content_type} 콘텐츠 아이디어</h4>
                            <div style='white-space: pre-wrap; line-height: 1.6;'>{idea}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # 콘텐츠 제작 통계
        st.markdown("### 📊 콘텐츠 제작 통계")
        
        if hasattr(chatbot, 'knowledge_base') and chatbot.knowledge_base.get('top_keywords'):
            keywords = list(chatbot.knowledge_base['top_keywords'].items())[:6]
            
            if keywords:
                df_keywords = pd.DataFrame(keywords, columns=['키워드', '빈도'])
                fig = px.scatter(df_keywords, x='키워드', y='빈도', size='빈도',
                              title=f"{persona['name']}의 콘텐츠 키워드 분포",
                              color='빈도',
                              color_continuous_scale='viridis')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    def save_chat_history(self, persona_name):
        """대화 기록 저장"""
        if st.session_state.chat_history:
            filename = f"chat_history_{persona_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=2)
            st.success(f"대화 기록이 {filename}에 저장되었습니다!")
    
    def run(self):
        """메인 실행 함수"""
        self.setup_page_config()
        self.setup_css()
        
        # 헤더
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1);'>
            <h1>🎭 Gen Z 인플루언서 페르소나봇</h1>
            <p>다양한 라이프스타일을 가진 Gen Z 인플루언서들과 대화하고, 트렌드를 분석하고, 라이프스타일 가이드를 받아보세요!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 사이드바
        self.show_sidebar()
        
        # 메인 탭
        tab1, tab2, tab3, tab4 = st.tabs(["💬 대화", "📈 트렌드 분석", "🏠 라이프스타일 가이드", "🎬 콘텐츠 제작"])
        
        with tab1:
            self.show_chat_interface()
        
        with tab2:
            self.show_trend_analysis()
        
        with tab3:
            self.show_lifestyle_guide()
        
        with tab4:
            self.show_content_creation()

# 실행
if __name__ == "__main__":
    try:
        gui = EnhancedPersonaGUI()
        gui.run()
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        st.error("OpenAI API 키가 설정되어 있는지 확인해주세요.")
