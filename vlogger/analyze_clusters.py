# -*- coding: utf-8 -*-
import pandas as pd
import json

def analyze_clusters():
    """클러스터 분석 및 페르소나 생성"""
    
    # 데이터 로드
    df = pd.read_csv('persona_clusters.csv')
    
    print("=" * 80)
    print("Gen Z 인플루언서 페르소나 클러스터링 결과")
    print("=" * 80)
    
    # 클러스터별 분석
    cluster_analysis = {}
    
    for cluster_id in sorted(df['cluster'].unique()):
        cluster_data = df[df['cluster'] == cluster_id]
        
        print(f"\n클러스터 {cluster_id}: {len(cluster_data)}개 채널")
        print("-" * 60)
        
        # 채널 목록
        channels = cluster_data['channel_name'].tolist()
        print(f"채널들: {', '.join(channels)}")
        
        # 평균 통계
        avg_views = cluster_data['avg_views'].mean()
        avg_likes = cluster_data['avg_likes'].mean()
        print(f"평균 조회수: {avg_views:,.0f}")
        print(f"평균 좋아요: {avg_likes:,.0f}")
        
        # 라이프스타일 액티비티 분석
        activity_columns = [
            'cooking_eating', 'reading_journaling', 'shopping_haul', 
            'mindfulness_relaxation', 'exercise_fitness', 'beauty_skincare',
            'travel_adventure', 'art_craft', 'gaming', 'music',
            'pet_care', 'home_decor', 'tech_gadgets', 'fashion',
            'photography', 'social_events'
        ]
        
        # 클러스터별 평균 액티비티 점수
        avg_activities = cluster_data[activity_columns].mean().sort_values(ascending=False)
        
        print("\n주요 라이프스타일 액티비티 (상위 5개):")
        for i, (activity, score) in enumerate(avg_activities.head(5).items(), 1):
            activity_names = {
                'cooking_eating': '요리 & 식사',
                'reading_journaling': '독서 & 저널링',
                'shopping_haul': '쇼핑 & 하울',
                'mindfulness_relaxation': '마인드풀니스 & 휴식',
                'exercise_fitness': '운동 & 피트니스',
                'beauty_skincare': '뷰티 & 스킨케어',
                'travel_adventure': '여행 & 어드벤처',
                'art_craft': '예술 & 크래프트',
                'gaming': '게임',
                'music': '음악',
                'pet_care': '반려동물 케어',
                'home_decor': '홈 데코',
                'tech_gadgets': '테크 & 가젯',
                'fashion': '패션',
                'photography': '사진',
                'social_events': '사교 활동'
            }
            print(f"  {i}. {activity_names.get(activity, activity)}: {score:.1f}점")
        
        # 클러스터 특징 분석
        cluster_characteristics = analyze_cluster_characteristics(cluster_id, avg_activities, channels)
        
        cluster_analysis[f'cluster_{cluster_id}'] = {
            'cluster_id': cluster_id,
            'channel_count': len(cluster_data),
            'channels': channels,
            'avg_views': avg_views,
            'avg_likes': avg_likes,
            'top_activities': avg_activities.head(5).to_dict(),
            'characteristics': cluster_characteristics
        }
    
    # 결과 저장
    with open('cluster_analysis_manual.json', 'w', encoding='utf-8') as f:
        json.dump(cluster_analysis, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("분석 완료! cluster_analysis_manual.json 파일이 생성되었습니다.")
    print("=" * 80)

def analyze_cluster_characteristics(cluster_id, avg_activities, channels):
    """클러스터별 특징 분석"""
    
    # 상위 액티비티들
    top_activities = avg_activities.head(3)
    
    # 클러스터별 페르소나 생성
    personas = {
        0: {
            'name': 'Emma',
            'description': '다재다능한 라이프스타일 인플루언서',
            'characteristics': ['창의적', '다양한 관심사', '예술적 감성', '여행 애호가', '독서가']
        },
        1: {
            'name': 'Victoria',
            'description': '홈 & 뷰티 중심의 라이프스타일 인플루언서',
            'characteristics': ['홈 데코 전문', '뷰티 전문', '일상 공유', '실용적', '감성적']
        },
        2: {
            'name': 'Misha',
            'description': '활발한 콘텐츠 크리에이터',
            'characteristics': ['에너지틱', '창의적', '다양한 콘텐츠', '예술적', '활동적']
        },
        3: {
            'name': 'Philip',
            'description': '예술 & 크래프트 전문가',
            'characteristics': ['예술적', '창의적', '디테일 지향', '독창적', '감성적']
        },
        4: {
            'name': 'James',
            'description': '뷰티 & 패션 전문가',
            'characteristics': ['뷰티 전문', '패션 전문', '트렌드 민감', '스타일리시', '전문적']
        }
    }
    
    if cluster_id in personas:
        return personas[cluster_id]
    else:
        return {
            'name': f'Persona_{cluster_id}',
            'description': '특별한 라이프스타일을 가진 인플루언서',
            'characteristics': ['독특함', '개성적', '창의적']
        }

if __name__ == "__main__":
    analyze_clusters()
