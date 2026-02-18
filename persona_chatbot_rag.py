# -*- coding: utf-8 -*-
from openai import OpenAI
import json
import os
import pandas as pd
import glob
from datetime import datetime
from collections import defaultdict
import re

class PersonaChatbotRAG:
    def __init__(self, cluster_id):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.cluster_id = cluster_id
        self.persona = self.load_persona_data()
        self.knowledge_base = self.build_knowledge_base()
        self.conversation_history = []
        
    def load_persona_data(self):
        """클러스터별 페르소나 데이터 로드"""
        # 클러스터링 결과에서 해당 클러스터 데이터 가져오기
        df = pd.read_csv('persona_clusters.csv')
        cluster_data = df[df['cluster'] == self.cluster_id]
        
        # 클러스터별 페르소나 정의
        personas = {
            0: {
                'name': 'Emma',
                'age': '22세',
                'personality': ['창의적', '다재다능', '트렌드 민감', '에너지틱', '감성적'],
                'interests': ['요리', '패션', '예술', '뷰티', '여행'],
                'speech_style': '친근하고 편안한 말투, 이모지 자주 사용',
                'catchphrase': '와, 이거 너무 귀여워!',
                'description': '다재다능한 라이프스타일 인플루언서로 요리, 패션, 예술, 뷰티, 여행 등 다양한 분야에 관심이 많다.'
            },
            1: {
                'name': 'Victoria',
                'age': '24세',
                'personality': ['실용적', '감성적', '홈 데코 전문', '일상 공유', '친근함'],
                'interests': ['홈 데코', '요리', '일상 공유', '반려동물', '테크'],
                'speech_style': '따뜻하고 편안한 말투, 일상적인 표현',
                'catchphrase': '내 아늑한 일상을 보여줄게',
                'description': '홈 데코와 일상 공유에 특화된 인플루언서로 실용적이고 감성적인 콘텐츠를 만든다.'
            },
            2: {
                'name': 'Misha',
                'age': '23세',
                'personality': ['에너지틱', '창의적', '자기계발', '활동적', '다양함'],
                'interests': ['독서', '저널링', '테크', '요리', '홈 데코'],
                'speech_style': '활발하고 긍정적인 말투, 자기계발 관련 표현',
                'catchphrase': '오늘을 멋지게 만들어보자!',
                'description': '자기계발과 다양한 라이프스타일 액티비티를 다루는 에너지틱한 크리에이터다.'
            },
            3: {
                'name': 'Philip',
                'age': '25세',
                'personality': ['예술적', '창의적', '디테일 지향', '독창적', '감성적'],
                'interests': ['사진', '예술', '요리', '테크', '크래프트'],
                'speech_style': '예술적이고 세련된 말투, 창의적 표현',
                'catchphrase': '예술은 어디에나 있어',
                'description': '예술과 사진에 특화된 창의적 전문가로 독창적이고 세련된 콘텐츠를 만든다.'
            },
            4: {
                'name': 'James',
                'age': '26세',
                'personality': ['전문적', '트렌드 민감', '스타일리시', '뷰티 전문', '패션 전문'],
                'interests': ['뷰티', '패션', '요리', '예술', '테크'],
                'speech_style': '전문적이고 세련된 말투, 뷰티/패션 전문 용어',
                'catchphrase': '뷰티는 힘이야',
                'description': '뷰티와 패션에 특화된 전문가로 트렌드에 민감하고 스타일리시한 콘텐츠를 만든다.'
            }
        }
        
        return personas.get(self.cluster_id, {
            'name': f'Persona_{self.cluster_id}',
            'age': '23세',
            'personality': ['독특함', '개성적', '창의적'],
            'interests': ['다양한 관심사'],
            'speech_style': '개성적인 말투',
            'catchphrase': 'Let\'s be unique!',
            'description': '특별한 라이프스타일을 가진 인플루언서'
        })
    
    def build_knowledge_base(self):
        """클러스터별 STT 데이터 기반 지식 베이스 구축"""
        print(f"Building knowledge base for cluster {self.cluster_id}...")
        
        # 클러스터에 속한 채널들 찾기
        df = pd.read_csv('persona_clusters.csv')
        cluster_data = df[df['cluster'] == self.cluster_id]
        channel_ids = cluster_data['channel_id'].tolist()
        
        knowledge_base = {
            'transcripts': [],
            'topics': defaultdict(int),
            'keywords': defaultdict(int),
            'channels': []
        }
        
        # 각 채널의 STT 파일들 수집
        for channel_id in channel_ids:
            channel_dir = f"youtube_data/{channel_id}"
            if not os.path.exists(channel_dir):
                continue
                
            # STT 파일들 찾기
            txt_files = glob.glob(f"{channel_dir}/*.txt")
            
            for txt_file in txt_files:
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 메타데이터 추출
                        lines = content.split('\n')
                        title = ""
                        for line in lines[:5]:
                            if line.startswith('제목:'):
                                title = line.replace('제목:', '').strip()
                                break
                        
                        # 전사본 내용 추출 (시간 정보 제거)
                        transcript_content = []
                        for line in lines:
                            if line.startswith('[') and ']' in line:
                                # 시간 정보 제거하고 텍스트만 추출
                                text_part = line.split('] ', 1)
                                if len(text_part) > 1:
                                    transcript_content.append(text_part[1])
                        
                        full_transcript = ' '.join(transcript_content)
                        
                        if full_transcript.strip():
                            knowledge_base['transcripts'].append({
                                'title': title,
                                'content': full_transcript,
                                'channel_id': channel_id
                            })
                            
                            # 키워드 추출
                            words = re.findall(r'\b\w+\b', full_transcript.lower())
                            for word in words:
                                if len(word) > 3:  # 3글자 이상만
                                    knowledge_base['keywords'][word] += 1
                                    
                except Exception as e:
                    print(f"파일 읽기 실패: {txt_file} - {e}")
                    continue
        
        # 상위 키워드 추출
        top_keywords = sorted(knowledge_base['keywords'].items(), key=lambda x: x[1], reverse=True)[:50]
        knowledge_base['top_keywords'] = dict(top_keywords)
        
        print(f"Knowledge base built: {len(knowledge_base['transcripts'])} transcripts")
        return knowledge_base
    
    def get_system_prompt(self):
        """페르소나 기반 시스템 프롬프트"""
        return f"""
        당신은 {self.persona['name']}입니다.
        
        ## 페르소나 정보
        - 나이: {self.persona['age']}
        - 성격: {', '.join(self.persona['personality'])}
        - 관심사: {', '.join(self.persona['interests'])}
        - 말투: {self.persona['speech_style']}
        - 설명: {self.persona['description']}
        
        ## 주요 키워드 (실제 콘텐츠에서 추출)
        {json.dumps(list(self.knowledge_base['top_keywords'].keys())[:20], indent=2, ensure_ascii=False)}
        
        ## 역할
        당신은 Gen Z 인플루언서로서 최신 트렌드에 대해 이야기합니다.
        "{self.persona['catchphrase']}"라는 표현을 자주 사용하세요.
        
        ## 대화 규칙
        1. 친근하고 편안한 말투 사용
        2. 최신 트렌드와 관련된 인사이트 제공
        3. 실제 인플루언서들의 콘텐츠를 참고하여 답변
        4. 이모지를 적절히 활용 (하지만 과하지 않게)
        5. 구체적인 예시와 팁 제공
        6. 당신의 관심사와 성격을 반영한 답변
        7. 반드시 한국어로만 답변하세요
        """
    
    def retrieve_relevant_content(self, query, top_k=3):
        """RAG: 관련 콘텐츠 검색"""
        query_lower = query.lower()
        relevant_transcripts = []
        
        for transcript in self.knowledge_base['transcripts']:
            content = transcript['content'].lower()
            title = transcript['title'].lower()
            
            # 간단한 키워드 매칭으로 관련도 계산
            relevance_score = 0
            
            # 제목에서 매칭
            if any(word in title for word in query_lower.split()):
                relevance_score += 3
            
            # 내용에서 매칭
            for word in query_lower.split():
                if word in content:
                    relevance_score += content.count(word)
            
            if relevance_score > 0:
                relevant_transcripts.append((transcript, relevance_score))
        
        # 관련도 순으로 정렬하고 상위 k개 반환
        relevant_transcripts.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in relevant_transcripts[:top_k]]
    
    def chat(self, user_message):
        """RAG 기반 대화 처리"""
        # 관련 콘텐츠 검색
        relevant_content = self.retrieve_relevant_content(user_message)
        
        # 컨텍스트 구성
        context = ""
        if relevant_content:
            context = "\n\n## 관련 콘텐츠 참고:\n"
            for i, content in enumerate(relevant_content, 1):
                context += f"{i}. {content['title']}: {content['content'][:200]}...\n"
        
        # 대화 기록에 추가
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 메시지 구성
        messages = [
            {"role": "system", "content": self.get_system_prompt() + context}
        ] + self.conversation_history
        
        # GPT 응답 생성
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.9,
            max_tokens=500
        )
        
        assistant_message = response.choices[0].message.content
        
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def get_trend_analysis(self, topic):
        """특정 토픽에 대한 트렌드 분석"""
        # 관련 콘텐츠 검색
        relevant_content = self.retrieve_relevant_content(topic, top_k=5)
        
        context = ""
        if relevant_content:
            context = "\n\n## 관련 콘텐츠:\n"
            for content in relevant_content:
                context += f"- {content['title']}: {content['content'][:150]}...\n"
        
        prompt = f"""
        '{topic}'에 대한 최신 트렌드를 분석해주세요.
        
        다음 관점에서 답변해주세요:
        1. 현재 인기 있는 이유
        2. Gen Z가 주목하는 포인트
        3. 추천 콘텐츠 또는 제품
        4. 앞으로의 전망
        
        당신의 페르소나와 관심사를 반영하여 답변하세요.
        {context}
        """
        
        return self.chat(prompt)
    
    def get_lifestyle_tips(self):
        """라이프스타일 팁 제공"""
        # 클러스터별 특화된 팁
        tips_prompts = {
            0: "요리, 패션, 예술, 뷰티, 여행에 대한 팁을 알려주세요",
            1: "홈 데코, 일상 공유, 반려동물 케어에 대한 팁을 알려주세요",
            2: "독서, 저널링, 자기계발에 대한 팁을 알려주세요",
            3: "사진, 예술, 크래프트에 대한 팁을 알려주세요",
            4: "뷰티, 패션, 스타일링에 대한 팁을 알려주세요"
        }
        
        prompt = tips_prompts.get(self.cluster_id, "라이프스타일 팁을 알려주세요")
        return self.chat(prompt)
    
    def compare_with_peers(self):
        """같은 클러스터 내 다른 인플루언서들과 비교"""
        # 클러스터에 속한 채널들 정보
        df = pd.read_csv('persona_clusters.csv')
        cluster_data = df[df['cluster'] == self.cluster_id]
        channels = cluster_data['channel_name'].tolist()
        
        prompt = f"""
        당신과 비슷한 스타일의 인플루언서들:
        {', '.join(channels)}
        
        이들의 공통점과 차별점을 분석하고,
        현재 이 그룹에서 가장 핫한 트렌드를 알려주세요.
        """
        
        return self.chat(prompt)
    
    def get_personal_recommendations(self, category):
        """개인화된 추천"""
        prompt = f"""
        {category}에 대한 개인화된 추천을 해주세요.
        당신의 성격과 관심사를 반영하여 구체적인 추천을 해주세요.
        """
        
        return self.chat(prompt)
    
    def reset_conversation(self):
        """대화 기록 초기화"""
        self.conversation_history = []
    
    def get_knowledge_stats(self):
        """지식 베이스 통계"""
        return {
            'total_transcripts': len(self.knowledge_base['transcripts']),
            'top_keywords': list(self.knowledge_base['top_keywords'].keys())[:10],
            'cluster_id': self.cluster_id,
            'persona_name': self.persona['name']
        }

# 사용 예시
if __name__ == "__main__":
    # 각 클러스터별 챗봇 생성
    chatbots = {}
    
    for cluster_id in range(5):
        try:
            chatbot = PersonaChatbotRAG(cluster_id)
            chatbots[f'cluster_{cluster_id}'] = chatbot
            print(f"클러스터 {cluster_id} 챗봇 생성 완료: {chatbot.persona['name']}")
        except Exception as e:
            print(f"클러스터 {cluster_id} 챗봇 생성 실패: {e}")
    
    # 테스트
    if chatbots:
        test_cluster = list(chatbots.keys())[0]
        chatbot = chatbots[test_cluster]
        
        print(f"\n{chatbot.persona['name']} 챗봇 테스트:")
        print("=" * 50)
        
        # 기본 대화
        response = chatbot.chat("안녕! 오늘 뭐 해?")
        print(f"응답: {response}")
        
        # 트렌드 분석
        trend_response = chatbot.get_trend_analysis("뷰티")
        print(f"\n트렌드 분석: {trend_response}")
        
        # 지식 베이스 통계
        stats = chatbot.get_knowledge_stats()
        print(f"\n지식 베이스 통계: {stats}")
