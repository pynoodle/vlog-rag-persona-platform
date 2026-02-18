# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
from datetime import datetime
from cluster_chatbots import ChatbotManager

class SimplePersonaGUI:
    def __init__(self):
        self.manager = ChatbotManager()
        
        # 페르소나 정보
        self.personas = {
            0: {
                'name': 'Emma',
                'avatar': '👩‍🍳',
                'description': '다재다능한 라이프스타일 인플루언서',
                'specialty': '요리, 패션, 예술, 뷰티, 여행',
                'catchphrase': 'OMG, this is so cute!'
            },
            1: {
                'name': 'Victoria',
                'avatar': '🏠',
                'description': '홈 & 뷰티 중심 라이프스타일 인플루언서',
                'specialty': '홈 데코, 일상 공유, 반려동물 케어',
                'catchphrase': 'Let me show you my cozy life!'
            },
            2: {
                'name': 'Misha',
                'avatar': '📚',
                'description': '활발한 콘텐츠 크리에이터',
                'specialty': '독서, 저널링, 자기계발, 테크',
                'catchphrase': 'Let\'s make today amazing!'
            },
            3: {
                'name': 'Philip',
                'avatar': '📸',
                'description': '예술 & 크래프트 전문가',
                'specialty': '사진, 예술, 크래프트, 요리',
                'catchphrase': 'Art is everywhere'
            },
            4: {
                'name': 'James',
                'avatar': '💄',
                'description': '뷰티 & 패션 전문가',
                'specialty': '뷰티, 패션, 스타일링',
                'catchphrase': 'Beauty is power'
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
    
    def show_sidebar(self):
        """사이드바 표시"""
        with st.sidebar:
            st.title("🎭 페르소나 선택")
            
            # 페르소나 선택
            for cluster_id, persona in self.personas.items():
                if st.button(f"{persona['avatar']} {persona['name']}", key=f"persona_{cluster_id}", use_container_width=True):
                    st.session_state.selected_persona = cluster_id
                    st.rerun()
            
            st.markdown("---")
            
            # 현재 선택된 페르소나 정보
            if 'selected_persona' in st.session_state:
                persona = self.personas[st.session_state.selected_persona]
                st.markdown(f"""
                **{persona['name']}**
                - {persona['description']}
                - 전문분야: {persona['specialty']}
                - 대표 문구: "{persona['catchphrase']}"
                """)
    
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
            st.markdown(f"<div style='font-size: 4rem; text-align: center;'>{persona['avatar']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            **{persona['name']}** ({persona['description']})
            - 전문분야: {persona['specialty']}
            - 대표 문구: "{persona['catchphrase']}"
            """)
        
        st.markdown("---")
        
        # 채팅 기록 표시
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # 채팅 기록 컨테이너
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**👤 당신:** {message['content']}")
            else:
                st.markdown(f"**🤖 {persona['name']}:** {message['content']}")
        
        # 메시지 입력
        st.markdown("---")
        user_input = st.text_input("메시지를 입력하세요:", key="user_input", placeholder="안녕! 오늘 뭐 해?")
        
        col1, col2, col3 = st.columns([2, 1, 1])
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
    
    def send_message(self, message, chatbot, persona):
        """메시지 전송"""
        # 사용자 메시지 추가
        st.session_state.chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        # 봇 응답 생성
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
            trend_topic = st.text_input("분석하고 싶은 트렌드 주제를 입력하세요:", placeholder="뷰티, 패션, 요리, 홈데코 등")
        with col2:
            if st.button("🔍 분석", use_container_width=True):
                if trend_topic:
                    with st.spinner("트렌드 분석 중..."):
                        analysis = chatbot.get_trend_analysis(trend_topic)
                        
                        st.markdown(f"""
                        **📊 {trend_topic} 트렌드 분석**
                        *분석자: {persona['name']} ({persona['specialty']})*
                        
                        {analysis}
                        """)
        
        # 페르소나별 트렌드 인사이트
        st.markdown("### 🎯 페르소나별 특화 트렌드")
        
        trend_insights = {
            0: "요리, 패션, 예술, 뷰티, 여행 분야의 최신 트렌드",
            1: "홈 데코, 일상 공유, 반려동물 케어 관련 트렌드",
            2: "독서, 저널링, 자기계발, 테크 분야 트렌드",
            3: "사진, 예술, 크래프트, 창의적 활동 트렌드",
            4: "뷰티, 패션, 스타일링 관련 트렌드"
        }
        
        st.info(f"💡 {persona['name']}의 전문분야: {trend_insights[st.session_state.selected_persona]}")
    
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
                **🌟 {persona['name']}의 라이프스타일 가이드**
                *전문분야: {persona['specialty']}*
                
                {tips}
                """)
        
        # 페르소나별 특화 가이드
        st.markdown("### 🎯 전문분야별 가이드")
        
        guide_categories = {
            0: ["요리 초보자를 위한 레시피", "패션 스타일링 팁", "예술 활동 아이디어"],
            1: ["홈 데코 아이디어", "일상 루틴 만들기", "반려동물 케어"],
            2: ["독서 방법", "저널링 기법", "자기계발 계획"],
            3: ["사진 촬영 기법", "예술 프로젝트", "창의적 요리"],
            4: ["뷰티 루틴", "패션 코디", "스타일링 팁"]
        }
        
        categories = guide_categories[st.session_state.selected_persona]
        
        for category in categories:
            if st.button(f"📋 {category}", use_container_width=True):
                with st.spinner(f"{category} 가이드 생성 중..."):
                    guide = chatbot.chat(f"{category}에 대한 상세한 가이드를 알려주세요!")
                    
                    st.markdown(f"""
                    **📋 {category}**
                    
                    {guide}
                    """)
    
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
            content_topic = st.text_input("콘텐츠 주제를 입력하세요:", placeholder="요리, 패션, 뷰티, 홈데코 등")
        with col2:
            if st.button("💡 아이디어 생성", use_container_width=True):
                if content_topic:
                    with st.spinner("콘텐츠 아이디어 생성 중..."):
                        idea = chatbot.chat(f"{content_topic}에 대한 인플루언서 스타일의 콘텐츠 아이디어를 알려주세요!")
                        
                        st.markdown(f"""
                        **🎬 {content_topic} 콘텐츠 아이디어**
                        *제작자: {persona['name']} 스타일*
                        
                        {idea}
                        """)
        
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
            0: ["요리 레시피", "패션 스타일링", "여행 브이로그", "예술 DIY"],
            1: ["홈 데코 투어", "일상 루틴", "반려동물 케어", "아늑한 라이프"],
            2: ["독서 리뷰", "저널링 방법", "자기계발 팁", "테크 리뷰"],
            3: ["사진 촬영", "예술 프로젝트", "크래프트 DIY", "창의적 요리"],
            4: ["뷰티 튜토리얼", "패션 코디", "스타일링 팁", "메이크업 리뷰"]
        }
        
        types = content_types[st.session_state.selected_persona]
        
        for content_type in types:
            if st.button(f"🎬 {content_type}", use_container_width=True):
                with st.spinner(f"{content_type} 콘텐츠 아이디어 생성 중..."):
                    idea = chatbot.chat(f"{content_type}에 대한 인플루언서 콘텐츠 아이디어를 구체적으로 알려주세요!")
                    
                    st.markdown(f"""
                    **🎬 {content_type} 콘텐츠 아이디어**
                    
                    {idea}
                    """)
    
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
        
        # 헤더
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 2rem;'>
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
        gui = SimplePersonaGUI()
        gui.run()
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        st.error("OpenAI API 키가 설정되어 있는지 확인해주세요.")
