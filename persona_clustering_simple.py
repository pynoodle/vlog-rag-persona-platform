# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import json
import os
import glob
from collections import Counter, defaultdict
from openai import OpenAI
import re

class PersonaClusterer:
    def __init__(self, data_path='youtube_data'):
        self.data_path = data_path
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # 라이프스타일 액티비티 키워드 정의
        self.activity_keywords = {
            'cooking_eating': [
                'cook', 'cooking', 'recipe', 'food', 'eat', 'eating', 'meal', 'lunch', 'dinner', 'breakfast',
                'kitchen', 'baking', 'bake', 'snack', 'hungry', 'taste', 'delicious', 'yummy', '요리', '먹', '밥', '식사'
            ],
            'reading_journaling': [
                'read', 'reading', 'book', 'books', 'journal', 'journaling', 'write', 'writing', 'study', 'studying',
                'learn', 'learning', 'note', 'notes', 'diary', '독서', '책', '일기', '공부'
            ],
            'shopping_haul': [
                'shop', 'shopping', 'haul', 'buy', 'buying', 'purchase', 'store', 'mall', 'online', 'amazon',
                'order', 'delivery', 'package', 'unboxing', '쇼핑', '구매', '하울'
            ],
            'mindfulness_relaxation': [
                'relax', 'relaxing', 'meditation', 'meditate', 'mindful', 'mindfulness', 'calm', 'peaceful',
                'stress', 'anxiety', 'breath', 'breathing', 'yoga', 'zen', '휴식', '명상', '마음'
            ],
            'exercise_fitness': [
                'exercise', 'workout', 'gym', 'fitness', 'run', 'running', 'walk', 'walking', 'dance', 'dancing',
                'stretch', 'stretching', 'cardio', 'strength', '운동', '헬스', '피트니스'
            ],
            'beauty_skincare': [
                'beauty', 'skincare', 'makeup', 'make up', 'skin', 'face', 'routine', 'morning routine',
                'night routine', 'cleanser', 'moisturizer', 'serum', 'mask', '뷰티', '스킨케어', '화장'
            ],
            'travel_adventure': [
                'travel', 'trip', 'vacation', 'adventure', 'explore', 'exploring', 'journey', 'flight', 'plane',
                'hotel', 'airbnb', 'destination', '여행', '휴가', '여행'
            ],
            'art_craft': [
                'art', 'artistic', 'craft', 'crafting', 'draw', 'drawing', 'paint', 'painting', 'create',
                'creative', 'design', 'diy', 'project', '예술', '그림', '만들기'
            ],
            'gaming': [
                'game', 'gaming', 'play', 'playing', 'video game', 'console', 'nintendo', 'playstation',
                'xbox', 'pc', 'mobile game', '게임', '플레이'
            ],
            'music': [
                'music', 'song', 'songs', 'sing', 'singing', 'dance', 'dancing', 'concert', 'album',
                'playlist', 'spotify', '음악', '노래', '춤'
            ],
            'pet_care': [
                'pet', 'pets', 'dog', 'cat', 'puppy', 'kitten', 'animal', 'animals', 'care', 'walk',
                'feeding', 'feed', '반려동물', '강아지', '고양이'
            ],
            'home_decor': [
                'home', 'house', 'room', 'decor', 'decoration', 'furniture', 'interior', 'design',
                'cozy', 'aesthetic', 'vibe', '홈', '집', '인테리어', '꾸미기'
            ],
            'tech_gadgets': [
                'phone', 'smartphone', 'iphone', 'android', 'tech', 'technology', 'gadget', 'device',
                'app', 'apps', 'digital', 'online', '스마트폰', '폰', '기술'
            ],
            'fashion': [
                'fashion', 'style', 'outfit', 'clothes', 'clothing', 'dress', 'shirt', 'pants', 'shoes',
                'accessories', 'jewelry', '패션', '옷', '스타일'
            ],
            'photography': [
                'photo', 'photos', 'picture', 'pictures', 'camera', 'photography', 'photographer',
                'instagram', 'social media', '사진', '카메라'
            ],
            'social_events': [
                'party', 'celebration', 'event', 'meet', 'meeting', 'friend', 'friends', 'social',
                'hangout', 'gathering', '파티', '친구', '모임'
            ]
        }
    
    def load_channel_data(self):
        """채널 통계 데이터 로드"""
        try:
            channels = pd.read_csv('channel_stats.csv')
            print(f"채널 통계 로드 완료: {len(channels)}개 채널")
            return channels
        except FileNotFoundError:
            print("ERROR: channel_stats.csv 파일을 찾을 수 없습니다.")
            return None
    
    def extract_channel_features(self, channel_id, channel_name):
        """특정 채널의 라이프스타일 특징 추출"""
        print(f"채널 특징 추출 중: {channel_name}")
        
        # 기본 특징 초기화
        features = {
            'channel_id': channel_id,
            'channel_name': channel_name,
            'total_videos': 0,
            'total_stt_files': 0,
            'total_views': 0,
            'avg_views': 0,
            'total_likes': 0,
            'avg_likes': 0,
            'total_comments': 0,
            'avg_comments': 0
        }
        
        # 라이프스타일 액티비티 특징 초기화
        for activity in self.activity_keywords.keys():
            features[activity] = 0
        
        # 채널 디렉토리 경로
        channel_dir = os.path.join(self.data_path, channel_id)
        
        if not os.path.exists(channel_dir):
            print(f"WARNING: 채널 디렉토리 없음: {channel_dir}")
            return features
        
        # 채널 정보 로드
        channel_info_file = os.path.join(channel_dir, 'channel_info.json')
        if os.path.exists(channel_info_file):
            with open(channel_info_file, 'r', encoding='utf-8') as f:
                channel_info = json.load(f)
                features['total_videos'] = channel_info.get('total_videos_collected', 0)
        
        # STT 파일들 처리
        txt_files = glob.glob(os.path.join(channel_dir, "*.txt"))
        features['total_stt_files'] = len(txt_files)
        
        # 각 STT 파일에서 키워드 추출
        total_content = ""
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    total_content += content + " "
            except Exception as e:
                print(f"WARNING: 파일 읽기 실패: {txt_file} - {e}")
                continue
        
        # 각 액티비티별 키워드 카운트
        for activity, keywords in self.activity_keywords.items():
            count = 0
            for keyword in keywords:
                count += total_content.count(keyword.lower())
            features[activity] = count
        
        # 채널 통계에서 추가 정보 가져오기
        channels_df = self.load_channel_data()
        if channels_df is not None:
            channel_row = channels_df[channels_df['채널ID'] == channel_id]
            if not channel_row.empty:
                features['total_views'] = int(channel_row['총조회수'].iloc[0])
                features['avg_views'] = int(channel_row['평균조회수'].iloc[0])
                features['total_likes'] = int(channel_row['총좋아요'].iloc[0])
                features['avg_likes'] = int(channel_row['평균좋아요'].iloc[0])
                features['total_comments'] = int(channel_row['총댓글'].iloc[0])
                features['avg_comments'] = int(channel_row['평균댓글'].iloc[0])
        
        return features
    
    def load_lifestyle_data(self):
        """모든 채널의 라이프스타일 데이터 로드"""
        print("라이프스타일 데이터 로딩 시작...")
        
        channels_df = self.load_channel_data()
        if channels_df is None:
            return None
        
        lifestyle_features = []
        
        for idx, row in channels_df.iterrows():
            channel_id = row['채널ID']
            channel_name = row['채널명']
            
            features = self.extract_channel_features(channel_id, channel_name)
            lifestyle_features.append(features)
            
            if (idx + 1) % 10 == 0:
                print(f"진행률: {idx + 1}/{len(channels_df)} 채널 처리 완료")
        
        df = pd.DataFrame(lifestyle_features)
        print(f"라이프스타일 데이터 로드 완료: {len(df)}개 채널")
        return df
    
    def perform_clustering(self, n_clusters=5):
        """K-means 클러스터링 수행"""
        print(f"{n_clusters}개 클러스터로 클러스터링 시작...")
        
        df = self.load_lifestyle_data()
        if df is None:
            return None, None, None
        
        # 클러스터링용 특징 선택 (라이프스타일 액티비티만)
        activity_columns = list(self.activity_keywords.keys())
        X = df[activity_columns].copy()
        
        # 정규화
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 클러스터링
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(X_scaled)
        
        # PCA로 차원 축소 (시각화용)
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        df['pca1'] = X_pca[:, 0]
        df['pca2'] = X_pca[:, 1]
        
        print("클러스터링 완료!")
        print("클러스터별 채널 수:")
        for cluster_id in sorted(df['cluster'].unique()):
            count = len(df[df['cluster'] == cluster_id])
            print(f"   클러스터 {cluster_id}: {count}개 채널")
        
        return df, kmeans, scaler
    
    def analyze_cluster_characteristics(self, df):
        """각 클러스터의 특징 분석"""
        print("클러스터 특징 분석 중...")
        
        cluster_analysis = {}
        activity_columns = list(self.activity_keywords.keys())
        
        for cluster_id in sorted(df['cluster'].unique()):
            cluster_data = df[df['cluster'] == cluster_id]
            
            # 클러스터별 평균 액티비티 점수
            avg_activities = cluster_data[activity_columns].mean().sort_values(ascending=False)
            
            # 상위 5개 액티비티
            top_activities = avg_activities.head(5)
            
            # 클러스터 통계
            stats = {
                'cluster_id': cluster_id,
                'channel_count': len(cluster_data),
                'channels': cluster_data['channel_name'].tolist(),
                'avg_total_views': cluster_data['total_views'].mean(),
                'avg_avg_views': cluster_data['avg_views'].mean(),
                'avg_total_likes': cluster_data['total_likes'].mean(),
                'avg_avg_likes': cluster_data['avg_likes'].mean(),
                'top_activities': top_activities.to_dict(),
                'activity_scores': avg_activities.to_dict()
            }
            
            cluster_analysis[f'cluster_{cluster_id}'] = stats
        
        return cluster_analysis
    
    def generate_cluster_personas(self, cluster_analysis):
        """각 클러스터의 페르소나 생성"""
        print("페르소나 생성 중...")
        
        personas = {}
        
        for cluster_key, cluster_data in cluster_analysis.items():
            cluster_id = cluster_data['cluster_id']
            top_activities = cluster_data['top_activities']
            channels = cluster_data['channels']
            
            # GPT로 페르소나 생성
            prompt = f"""
            다음은 Gen Z 인플루언서 클러스터의 주요 라이프스타일 활동입니다:
            
            클러스터 {cluster_id}:
            - 채널 수: {cluster_data['channel_count']}개
            - 대표 채널들: {', '.join(channels[:5])}
            - 주요 활동 (점수 순):
            {chr(10).join([f"  - {activity}: {score:.1f}점" for activity, score in top_activities.items()])}
            
            이 클러스터를 대표하는 페르소나를 생성해주세요:
            1. 페르소나 이름 (창의적이고 기억하기 쉬운 이름)
            2. 나이대 (Gen Z, 18-26세)
            3. 성격 특징 (5가지)
            4. 주요 관심사 (5가지)
            5. 말투 특징 (3가지)
            6. 대표 문구 (페르소나가 자주 사용하는 표현 3개)
            7. 라이프스타일 설명 (2-3문장)
            8. 콘텐츠 스타일 (2-3문장)
            
            JSON 형식으로 답변해주세요.
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8
                )
                
                persona = json.loads(response.choices[0].message.content)
                persona['cluster_id'] = cluster_id
                persona['channels'] = channels
                persona['channel_count'] = cluster_data['channel_count']
                persona['top_activities'] = top_activities
                persona['stats'] = {
                    'avg_views': cluster_data['avg_avg_views'],
                    'avg_likes': cluster_data['avg_avg_likes']
                }
                
                personas[f'persona_{cluster_id}'] = persona
                
                print(f"클러스터 {cluster_id} 페르소나 생성 완료: {persona.get('name', 'Unknown')}")
                
            except Exception as e:
                print(f"ERROR: 클러스터 {cluster_id} 페르소나 생성 실패: {e}")
                continue
        
        return personas
    
    def save_results(self, df, personas, cluster_analysis):
        """결과 저장"""
        print("결과 저장 중...")
        
        # 클러스터링 결과 CSV 저장
        df.to_csv('persona_clusters.csv', index=False, encoding='utf-8-sig')
        print("persona_clusters.csv 저장 완료")
        
        # 페르소나 정보 JSON 저장
        with open('personas.json', 'w', encoding='utf-8') as f:
            json.dump(personas, f, ensure_ascii=False, indent=2)
        print("personas.json 저장 완료")
        
        # 클러스터 분석 결과 저장
        with open('cluster_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(cluster_analysis, f, ensure_ascii=False, indent=2)
        print("cluster_analysis.json 저장 완료")
        
        # 요약 리포트 생성
        self.generate_summary_report(personas, cluster_analysis)
    
    def generate_summary_report(self, personas, cluster_analysis):
        """요약 리포트 생성"""
        print("요약 리포트 생성 중...")
        
        report = []
        report.append("=" * 80)
        report.append("Gen Z 인플루언서 페르소나 클러스터링 결과")
        report.append("=" * 80)
        report.append("")
        
        for persona_key, persona in personas.items():
            cluster_id = persona['cluster_id']
            report.append(f"페르소나 {cluster_id}: {persona.get('name', 'Unknown')}")
            report.append("-" * 60)
            report.append(f"채널 수: {persona['channel_count']}개")
            report.append(f"대표 채널: {', '.join(persona['channels'][:5])}")
            report.append(f"평균 조회수: {persona['stats']['avg_views']:,.0f}")
            report.append(f"평균 좋아요: {persona['stats']['avg_likes']:,.0f}")
            report.append("")
            
            if 'personality' in persona:
                report.append("성격 특징:")
                for trait in persona['personality']:
                    report.append(f"  - {trait}")
                report.append("")
            
            if 'interests' in persona:
                report.append("주요 관심사:")
                for interest in persona['interests']:
                    report.append(f"  - {interest}")
                report.append("")
            
            if 'speaking_style' in persona:
                report.append("말투 특징:")
                for style in persona['speaking_style']:
                    report.append(f"  - {style}")
                report.append("")
            
            if 'catchphrases' in persona:
                report.append("대표 문구:")
                for phrase in persona['catchphrases']:
                    report.append(f"  - \"{phrase}\"")
                report.append("")
            
            if 'lifestyle' in persona:
                report.append("라이프스타일:")
                report.append(f"  {persona['lifestyle']}")
                report.append("")
            
            if 'content_style' in persona:
                report.append("콘텐츠 스타일:")
                report.append(f"  {persona['content_style']}")
                report.append("")
            
            report.append("=" * 80)
            report.append("")
        
        # 파일로 저장
        with open('persona_summary_report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print("persona_summary_report.txt 저장 완료")
    
    def run_full_analysis(self, n_clusters=5):
        """전체 분석 실행"""
        print("Gen Z 인플루언서 페르소나 클러스터링 시작!")
        print("=" * 60)
        
        # 1. 클러스터링 수행
        df, kmeans, scaler = self.perform_clustering(n_clusters)
        if df is None:
            print("ERROR: 클러스터링 실패")
            return None
        
        # 2. 클러스터 특징 분석
        cluster_analysis = self.analyze_cluster_characteristics(df)
        
        # 3. 페르소나 생성
        personas = self.generate_cluster_personas(cluster_analysis)
        
        # 4. 결과 저장
        self.save_results(df, personas, cluster_analysis)
        
        print("\n분석 완료!")
        print("생성된 파일들:")
        print("  - persona_clusters.csv: 클러스터링 결과")
        print("  - personas.json: 페르소나 정보")
        print("  - cluster_analysis.json: 클러스터 분석")
        print("  - persona_summary_report.txt: 요약 리포트")
        
        return df, personas, cluster_analysis

# 실행
if __name__ == "__main__":
    # OpenAI API 키 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY 환경변수를 설정해주세요!")
        print("   export OPENAI_API_KEY=your-api-key-here")
        exit(1)
    
    # 클러스터링 실행
    clusterer = PersonaClusterer()
    results = clusterer.run_full_analysis(n_clusters=5)
    
    if results:
        df, personas, cluster_analysis = results
        print(f"\n최종 결과:")
        print(f"  - 총 {len(df)}개 채널 분석")
        print(f"  - {len(personas)}개 페르소나 생성")
        print(f"  - {len(cluster_analysis)}개 클러스터 분석")
