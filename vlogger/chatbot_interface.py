# -*- coding: utf-8 -*-
from cluster_chatbots import ChatbotManager
import json

class ChatbotInterface:
    """페르소나 챗봇 인터페이스"""
    
    def __init__(self):
        self.manager = ChatbotManager()
        self.current_chatbot = None
        self.chat_history = []
    
    def show_welcome(self):
        """환영 메시지 출력"""
        print("=" * 80)
        print("🎭 Gen Z 인플루언서 페르소나 챗봇")
        print("=" * 80)
        print("다양한 라이프스타일을 가진 Gen Z 인플루언서들과 대화해보세요!")
        print()
    
    def show_chatbot_list(self):
        """챗봇 목록 출력"""
        print("📋 사용 가능한 챗봇들:")
        print("-" * 50)
        
        for cluster_id in range(5):
            info = self.manager.get_chatbot_info(cluster_id)
            if info:
                print(f"{cluster_id}. {info['name']} ({info['age']})")
                print(f"   전문분야: {info['specialty']}")
                print(f"   타겟: {info['target_audience']}")
                print()
    
    def select_chatbot(self):
        """챗봇 선택"""
        while True:
            try:
                choice = input("챗봇을 선택하세요 (0-4): ").strip()
                cluster_id = int(choice)
                
                if 0 <= cluster_id <= 4:
                    self.current_chatbot = self.manager.select_chatbot(cluster_id)
                    info = self.manager.get_chatbot_info(cluster_id)
                    print(f"\n✅ {info['name']} 챗봇이 선택되었습니다!")
                    print(f"   {info['name']}: {info['specialty']}")
                    print(f"   지식베이스: {info['knowledge_stats']['total_transcripts']}개 전사본")
                    print("\n💬 대화를 시작하세요! (종료하려면 'quit' 입력)")
                    return True
                else:
                    print("❌ 0-4 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
            except Exception as e:
                print(f"❌ 오류: {e}")
    
    def start_chat(self):
        """대화 시작"""
        if not self.current_chatbot:
            print("❌ 먼저 챗봇을 선택해주세요.")
            return
        
        print(f"\n{self.current_chatbot.persona['name']}: 안녕! 나는 {self.current_chatbot.persona['name']}야! {self.current_chatbot.persona['catchphrase']}")
        
        while True:
            try:
                user_input = input(f"\n👤 당신: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '종료', '나가기']:
                    print(f"\n{self.current_chatbot.persona['name']}: 안녕! 또 만나자! 👋")
                    break
                
                if not user_input:
                    continue
                
                # 특별한 명령어 처리
                if user_input.startswith('/'):
                    self.handle_special_commands(user_input)
                    continue
                
                # 일반 대화
                response = self.manager.chat_with_selected(user_input)
                print(f"\n🤖 {self.current_chatbot.persona['name']}: {response}")
                
                # 대화 기록 저장
                self.chat_history.append({
                    'user': user_input,
                    'bot': response,
                    'chatbot': self.current_chatbot.persona['name']
                })
                
            except KeyboardInterrupt:
                print(f"\n\n{self.current_chatbot.persona['name']}: 안녕! 또 만나자! 👋")
                break
            except Exception as e:
                print(f"❌ 오류가 발생했습니다: {e}")
    
    def handle_special_commands(self, command):
        """특별한 명령어 처리"""
        if command == '/help':
            self.show_help()
        elif command == '/info':
            self.show_chatbot_info()
        elif command == '/stats':
            self.show_knowledge_stats()
        elif command == '/trend':
            self.get_trend_analysis()
        elif command == '/tips':
            self.get_lifestyle_tips()
        elif command == '/reset':
            self.reset_conversation()
        elif command == '/switch':
            self.switch_chatbot()
        else:
            print("❌ 알 수 없는 명령어입니다. /help를 입력하여 도움말을 확인하세요.")
    
    def show_help(self):
        """도움말 출력"""
        print("\n📖 사용 가능한 명령어:")
        print("  /help - 도움말 보기")
        print("  /info - 현재 챗봇 정보 보기")
        print("  /stats - 지식베이스 통계 보기")
        print("  /trend - 트렌드 분석 요청")
        print("  /tips - 라이프스타일 팁 요청")
        print("  /reset - 대화 기록 초기화")
        print("  /switch - 다른 챗봇으로 전환")
        print("  quit/exit - 대화 종료")
    
    def show_chatbot_info(self):
        """현재 챗봇 정보 출력"""
        if self.current_chatbot:
            info = self.manager.get_chatbot_info(self.current_chatbot.cluster_id)
            print(f"\n📋 {info['name']} 정보:")
            print(f"  - 나이: {info['age']}")
            print(f"  - 전문분야: {info['specialty']}")
            print(f"  - 타겟: {info['target_audience']}")
            print(f"  - 성격: {', '.join(self.current_chatbot.persona['personality'])}")
            print(f"  - 관심사: {', '.join(self.current_chatbot.persona['interests'])}")
            print(f"  - 대표 문구: \"{self.current_chatbot.persona['catchphrase']}\"")
    
    def show_knowledge_stats(self):
        """지식베이스 통계 출력"""
        if self.current_chatbot:
            stats = self.current_chatbot.get_knowledge_stats()
            print(f"\n📊 {stats['persona_name']} 지식베이스 통계:")
            print(f"  - 총 전사본 수: {stats['total_transcripts']}개")
            print(f"  - 상위 키워드: {', '.join(stats['top_keywords'][:10])}")
    
    def get_trend_analysis(self):
        """트렌드 분석 요청"""
        if self.current_chatbot:
            topic = input("분석하고 싶은 트렌드 주제를 입력하세요: ").strip()
            if topic:
                print(f"\n🔍 {topic} 트렌드 분석 중...")
                response = self.current_chatbot.get_trend_analysis(topic)
                print(f"\n🤖 {self.current_chatbot.persona['name']}: {response}")
    
    def get_lifestyle_tips(self):
        """라이프스타일 팁 요청"""
        if self.current_chatbot:
            print(f"\n💡 {self.current_chatbot.persona['name']}의 라이프스타일 팁:")
            response = self.current_chatbot.get_lifestyle_tips()
            print(f"\n🤖 {self.current_chatbot.persona['name']: {response}")
    
    def reset_conversation(self):
        """대화 기록 초기화"""
        if self.current_chatbot:
            self.current_chatbot.reset_conversation()
            self.chat_history = []
            print(f"\n✅ {self.current_chatbot.persona['name']}의 대화 기록이 초기화되었습니다.")
    
    def switch_chatbot(self):
        """다른 챗봇으로 전환"""
        print("\n🔄 다른 챗봇으로 전환합니다...")
        self.show_chatbot_list()
        if self.select_chatbot():
            print("✅ 챗봇이 전환되었습니다!")
    
    def save_chat_history(self):
        """대화 기록 저장"""
        if self.chat_history:
            filename = f"chat_history_{self.current_chatbot.persona['name'].lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            print(f"✅ 대화 기록이 {filename}에 저장되었습니다.")
    
    def run(self):
        """메인 실행 함수"""
        self.show_welcome()
        self.show_chatbot_list()
        
        if self.select_chatbot():
            try:
                self.start_chat()
            finally:
                # 대화 기록 저장
                if self.chat_history:
                    save_choice = input("\n💾 대화 기록을 저장하시겠습니까? (y/n): ").strip().lower()
                    if save_choice in ['y', 'yes', '예', '네']:
                        self.save_chat_history()

# 실행
if __name__ == "__main__":
    from datetime import datetime
    
    try:
        interface = ChatbotInterface()
        interface.run()
    except KeyboardInterrupt:
        print("\n\n👋 프로그램을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
