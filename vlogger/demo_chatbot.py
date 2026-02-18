# -*- coding: utf-8 -*-
from cluster_chatbots import ChatbotManager
import json

def demo_chatbots():
    """페르소나 챗봇 데모"""
    print("🎭 Gen Z 인플루언서 페르소나 챗봇 데모")
    print("=" * 60)
    
    # 챗봇 매니저 생성
    manager = ChatbotManager()
    
    # 각 챗봇별 데모 대화
    demos = [
        {
            'cluster_id': 0,
            'name': 'Emma',
            'questions': [
                "안녕! 오늘 뭐 해?",
                "요리 초보자인데 쉬운 레시피 추천해줘!",
                "지금 가장 핫한 패션 트렌드 알려줘!"
            ]
        },
        {
            'cluster_id': 1,
            'name': 'Victoria',
            'questions': [
                "홈 데코 팁 좀 알려줘!",
                "아늑한 집 만들기 어떻게 해?",
                "반려동물과 함께하는 일상은 어때?"
            ]
        },
        {
            'cluster_id': 2,
            'name': 'Misha',
            'questions': [
                "독서 추천해줘!",
                "저널링 어떻게 시작해?",
                "자기계발 뭐부터 해야 할까?"
            ]
        },
        {
            'cluster_id': 3,
            'name': 'Philip',
            'questions': [
                "예쁜 사진 찍는 방법 알려줘!",
                "집에서 할 수 있는 예술 활동 뭐가 있어?",
                "창의적인 요리 방법 추천해줘!"
            ]
        },
        {
            'cluster_id': 4,
            'name': 'James',
            'questions': [
                "뷰티 트렌드 알려줘!",
                "스킨케어 루틴 어떻게 해?",
                "나만의 스타일 만드는 방법은?"
            ]
        }
    ]
    
    for demo in demos:
        print(f"\n🤖 {demo['name']} 챗봇 데모")
        print("-" * 40)
        
        try:
            # 챗봇 선택
            chatbot = manager.select_chatbot(demo['cluster_id'])
            
            for i, question in enumerate(demo['questions'], 1):
                print(f"\n👤 질문 {i}: {question}")
                response = chatbot.chat(question)
                print(f"🤖 {demo['name']}: {response}")
                
                # 응답이 너무 길면 잘라서 표시
                if len(response) > 200:
                    print("   ... (응답이 길어서 일부만 표시)")
                
        except Exception as e:
            print(f"❌ {demo['name']} 챗봇 데모 실패: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 모든 챗봇 데모 완료!")
    print("=" * 60)
    
    # 챗봇 정보 요약
    print("\n📊 챗봇 정보 요약:")
    for cluster_id in range(5):
        info = manager.get_chatbot_info(cluster_id)
        if info:
            print(f"  {info['name']}: {info['knowledge_stats']['total_transcripts']}개 전사본")

def interactive_demo():
    """대화형 데모"""
    print("\n🎮 대화형 데모")
    print("=" * 40)
    
    manager = ChatbotManager()
    
    # 챗봇 선택
    print("사용할 챗봇을 선택하세요:")
    for cluster_id in range(5):
        info = manager.get_chatbot_info(cluster_id)
        if info:
            print(f"  {cluster_id}. {info['name']} - {info['specialty']}")
    
    try:
        choice = int(input("\n선택 (0-4): "))
        if 0 <= choice <= 4:
            chatbot = manager.select_chatbot(choice)
            info = manager.get_chatbot_info(choice)
            
            print(f"\n✅ {info['name']} 챗봇이 선택되었습니다!")
            print(f"전문분야: {info['specialty']}")
            print("대화를 시작하세요! (종료하려면 'quit' 입력)")
            
            while True:
                user_input = input(f"\n👤 당신: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '종료']:
                    print(f"\n🤖 {info['name']}: 안녕! 또 만나자! 👋")
                    break
                
                if user_input:
                    response = chatbot.chat(user_input)
                    print(f"\n🤖 {info['name']}: {response}")
        else:
            print("❌ 잘못된 선택입니다.")
    except (ValueError, KeyboardInterrupt):
        print("\n👋 데모를 종료합니다.")

if __name__ == "__main__":
    try:
        # 자동 데모 실행
        demo_chatbots()
        
        # 대화형 데모 실행 여부 확인
        choice = input("\n대화형 데모를 실행하시겠습니까? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '예', '네']:
            interactive_demo()
        
    except KeyboardInterrupt:
        print("\n👋 프로그램을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
