# -*- coding: utf-8 -*-
from persona_chatbot_rag import PersonaChatbotRAG
import json

class EmmaChatbot(PersonaChatbotRAG):
    """클러스터 0: Emma - 다재다능한 라이프스타일 인플루언서"""
    def __init__(self):
        super().__init__(0)
        self.specialty = "요리, 패션, 예술, 뷰티, 여행"
        self.target_audience = "다양한 관심사를 가진 Gen Z"
    
    def get_cooking_tips(self):
        """요리 팁 제공"""
        return self.chat("요리 초보자를 위한 쉬운 레시피와 팁을 알려주세요!")
    
    def get_fashion_advice(self):
        """패션 조언 제공"""
        return self.chat("지금 가장 핫한 패션 트렌드와 스타일링 팁을 알려주세요!")
    
    def get_art_inspiration(self):
        """예술 영감 제공"""
        return self.chat("집에서 할 수 있는 예술 활동과 DIY 프로젝트를 추천해주세요!")

class VictoriaChatbot(PersonaChatbotRAG):
    """클러스터 1: Victoria - 홈 & 뷰티 중심 라이프스타일 인플루언서"""
    def __init__(self):
        super().__init__(1)
        self.specialty = "홈 데코, 일상 공유, 반려동물 케어"
        self.target_audience = "홈 라이프에 관심 있는 Gen Z"
    
    def get_home_decor_tips(self):
        """홈 데코 팁 제공"""
        return self.chat("예쁘고 실용적인 홈 데코 아이디어를 알려주세요!")
    
    def get_daily_routine_advice(self):
        """일상 루틴 조언 제공"""
        return self.chat("생산적이고 행복한 일상 루틴을 만드는 방법을 알려주세요!")
    
    def get_pet_care_tips(self):
        """반려동물 케어 팁 제공"""
        return self.chat("반려동물과 함께하는 일상과 케어 팁을 알려주세요!")

class MishaChatbot(PersonaChatbotRAG):
    """클러스터 2: Misha - 활발한 콘텐츠 크리에이터"""
    def __init__(self):
        super().__init__(2)
        self.specialty = "독서, 저널링, 자기계발, 테크"
        self.target_audience = "자기계발에 관심 있는 Gen Z"
    
    def get_reading_recommendations(self):
        """독서 추천"""
        return self.chat("지금 읽어야 할 책과 독서 방법을 추천해주세요!")
    
    def get_journaling_guide(self):
        """저널링 가이드"""
        return self.chat("저널링을 시작하는 방법과 효과적인 저널링 팁을 알려주세요!")
    
    def get_self_improvement_tips(self):
        """자기계발 팁"""
        return self.chat("성장하는 Gen Z가 해야 할 자기계발 활동을 알려주세요!")
    
    def get_tech_recommendations(self):
        """테크 추천"""
        return self.chat("생산성을 높이는 앱과 테크 도구를 추천해주세요!")

class PhilipChatbot(PersonaChatbotRAG):
    """클러스터 3: Philip - 예술 & 크래프트 전문가"""
    def __init__(self):
        super().__init__(3)
        self.specialty = "사진, 예술, 크래프트, 요리"
        self.target_audience = "창의적 활동에 관심 있는 Gen Z"
    
    def get_photography_tips(self):
        """사진 촬영 팁"""
        return self.chat("인스타그램에 올릴 예쁜 사진을 찍는 방법을 알려주세요!")
    
    def get_art_project_ideas(self):
        """예술 프로젝트 아이디어"""
        return self.chat("집에서 할 수 있는 예술 프로젝트와 크래프트 아이디어를 알려주세요!")
    
    def get_creative_cooking(self):
        """창의적 요리"""
        return self.chat("예술적인 플레이팅과 창의적인 요리 방법을 알려주세요!")

class JamesChatbot(PersonaChatbotRAG):
    """클러스터 4: James - 뷰티 & 패션 전문가"""
    def __init__(self):
        super().__init__(4)
        self.specialty = "뷰티, 패션, 스타일링"
        self.target_audience = "뷰티와 패션에 관심 있는 Gen Z"
    
    def get_beauty_tips(self):
        """뷰티 팁"""
        return self.chat("지금 가장 핫한 뷰티 트렌드와 메이크업 팁을 알려주세요!")
    
    def get_fashion_styling(self):
        """패션 스타일링"""
        return self.chat("나만의 스타일을 만드는 방법과 패션 코디 팁을 알려주세요!")
    
    def get_skincare_routine(self):
        """스킨케어 루틴"""
        return self.chat("효과적인 스킨케어 루틴과 제품 추천을 알려주세요!")

# 챗봇 팩토리 클래스
class ChatbotFactory:
    """클러스터별 챗봇 생성 팩토리"""
    
    @staticmethod
    def create_chatbot(cluster_id):
        """클러스터 ID에 따라 해당 챗봇 생성"""
        chatbots = {
            0: EmmaChatbot,
            1: VictoriaChatbot,
            2: MishaChatbot,
            3: PhilipChatbot,
            4: JamesChatbot
        }
        
        chatbot_class = chatbots.get(cluster_id)
        if chatbot_class:
            return chatbot_class()
        else:
            raise ValueError(f"클러스터 {cluster_id}에 해당하는 챗봇이 없습니다.")
    
    @staticmethod
    def get_all_chatbots():
        """모든 클러스터의 챗봇 생성"""
        chatbots = {}
        for cluster_id in range(5):
            try:
                chatbots[f'cluster_{cluster_id}'] = ChatbotFactory.create_chatbot(cluster_id)
            except Exception as e:
                print(f"Cluster {cluster_id} chatbot creation failed: {e}")
        return chatbots

# 챗봇 매니저 클래스
class ChatbotManager:
    """여러 챗봇을 관리하는 매니저"""
    
    def __init__(self):
        self.chatbots = ChatbotFactory.get_all_chatbots()
        self.current_chatbot = None
    
    def select_chatbot(self, cluster_id):
        """특정 클러스터의 챗봇 선택"""
        chatbot_key = f'cluster_{cluster_id}'
        if chatbot_key in self.chatbots:
            self.current_chatbot = self.chatbots[chatbot_key]
            return self.current_chatbot
        else:
            raise ValueError(f"클러스터 {cluster_id} 챗봇을 찾을 수 없습니다.")
    
    def get_chatbot_info(self, cluster_id):
        """챗봇 정보 조회"""
        chatbot = self.chatbots.get(f'cluster_{cluster_id}')
        if chatbot:
            return {
                'name': chatbot.persona['name'],
                'age': chatbot.persona['age'],
                'specialty': getattr(chatbot, 'specialty', '다양한 관심사'),
                'target_audience': getattr(chatbot, 'target_audience', 'Gen Z'),
                'knowledge_stats': chatbot.get_knowledge_stats()
            }
        return None
    
    def chat_with_selected(self, message):
        """선택된 챗봇과 대화"""
        if self.current_chatbot:
            return self.current_chatbot.chat(message)
        else:
            return "먼저 챗봇을 선택해주세요."
    
    def get_all_chatbot_info(self):
        """모든 챗봇 정보 조회"""
        info = {}
        for cluster_id in range(5):
            info[f'cluster_{cluster_id}'] = self.get_chatbot_info(cluster_id)
        return info

# 사용 예시
if __name__ == "__main__":
    # 챗봇 매니저 생성
    manager = ChatbotManager()
    
    # 모든 챗봇 정보 출력
    print("=" * 80)
    print("Gen Z 인플루언서 페르소나 챗봇들")
    print("=" * 80)
    
    for cluster_id in range(5):
        info = manager.get_chatbot_info(cluster_id)
        if info:
            print(f"\n클러스터 {cluster_id}: {info['name']}")
            print(f"  - 나이: {info['age']}")
            print(f"  - 전문분야: {info['specialty']}")
            print(f"  - 타겟: {info['target_audience']}")
            print(f"  - 지식베이스: {info['knowledge_stats']['total_transcripts']}개 전사본")
    
    # 특정 챗봇과 대화 테스트
    print("\n" + "=" * 80)
    print("챗봇 대화 테스트")
    print("=" * 80)
    
    # Emma 챗봇 선택
    emma = manager.select_chatbot(0)
    print(f"\n{emma.persona['name']} 챗봇과 대화:")
    response = manager.chat_with_selected("안녕! 오늘 뭐 해?")
    print(f"응답: {response}")
    
    # Victoria 챗봇 선택
    victoria = manager.select_chatbot(1)
    print(f"\n{victoria.persona['name']} 챗봇과 대화:")
    response = manager.chat_with_selected("홈 데코 팁 좀 알려줘!")
    print(f"응답: {response}")
