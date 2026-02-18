# -*- coding: utf-8 -*-
import os
import sys
import json
from collections import defaultdict, Counter

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class SmartphoneTopicAnalyzer:
    def __init__(self, input_file='smartphone_filtered_results.json'):
        self.input_file = input_file
        
        # 토픽별 키워드 정의
        self.topics = {
            '📦 언박싱/신제품 리뷰': {
                'keywords': ['unboxing', 'new phone', 'iphone 16', 'iphone 15', 'iphone 14', 
                           'galaxy', 'setup', 'first impressions', 'review', '언박싱'],
                'videos': []
            },
            '🎨 폰 커스터마이징/액세서리': {
                'keywords': ['case', 'screen protector', 'accessories', 'aesthetic', 'phone case',
                           'airpods', 'earbuds', 'widgets', 'wallpaper', '케이스', '액정보호필름'],
                'videos': []
            },
            '📱 스마트폰 사용 습관/디지털 웰빙': {
                'keywords': ['screen time', 'phone addiction', 'digital detox', 'reduce', 
                           'doom scrolling', 'mindful', 'phone control', 'notification', '스크린타임'],
                'videos': []
            },
            '📲 앱/소프트웨어/기능': {
                'keywords': ['app', 'ios', 'android', 'update', 'feature', 'siri', 
                           'whatsapp', 'instagram app', 'app store', 'google play', '앱'],
                'videos': []
            },
            '📸 사진/영상 촬영': {
                'keywords': ['camera', 'selfie', 'photo', 'video', 'filming', 
                           'recording', 'camera phone', '카메라', '셀카'],
                'videos': []
            },
            '🔋 배터리/충전': {
                'keywords': ['battery', 'charging', 'charger', 'power', 'battery life',
                           'fast charging', '배터리', '충전'],
                'videos': []
            },
            '💬 소셜미디어/커뮤니케이션': {
                'keywords': ['facetime', 'imessage', 'text message', 'messaging', 'call',
                           'social media', 'whatsapp', '메시지', '문자'],
                'videos': []
            },
            '🛍️ 쇼핑/하울': {
                'keywords': ['shopping', 'haul', 'buy', 'purchase', 'shop', 
                           'online shopping', 'mobile shopping'],
                'videos': []
            },
            '🎬 컨텐츠 제작/편집': {
                'keywords': ['filming', 'editing', 'content creator', 'vlog', 'youtube',
                           'camera phone', 'mobile', 'phone camera'],
                'videos': []
            },
            '💼 비즈니스/업무': {
                'keywords': ['business', 'work', 'meeting', 'office', 'productivity',
                           'zoom', 'phone call'],
                'videos': []
            },
            '🎮 엔터테인먼트': {
                'keywords': ['game', 'gaming', 'entertainment', 'music', 'streaming',
                           'watching', '5g'],
                'videos': []
            },
            '⚙️ 기술적 이슈/문제해결': {
                'keywords': ['problem', 'issue', 'fix', 'repair', 'broken', 'error',
                           'malfunction', 'troubleshoot'],
                'videos': []
            }
        }
    
    def load_data(self):
        """필터링된 데이터 로드"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def classify_video(self, video):
        """영상을 토픽별로 분류"""
        # 제목, 키워드, 세그먼트 텍스트 모두 검사
        text_to_search = video['video_title'].lower() + ' '
        text_to_search += ' '.join(video['found_keywords']).lower() + ' '
        
        # 세그먼트 텍스트도 추가
        for seg in video['keyword_segments']:
            text_to_search += seg['segment'].get('text', '').lower() + ' '
        
        # 각 토픽에 대해 매칭 점수 계산
        topic_scores = {}
        for topic_name, topic_data in self.topics.items():
            score = 0
            matched_keywords = []
            
            for keyword in topic_data['keywords']:
                if keyword.lower() in text_to_search:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                topic_scores[topic_name] = {
                    'score': score,
                    'matched_keywords': matched_keywords
                }
        
        return topic_scores
    
    def analyze_topics(self):
        """토픽 분석 실행"""
        data = self.load_data()
        
        print("\n" + "="*80)
        print("📊 스마트폰 관련 콘텐츠 토픽 분석")
        print("="*80 + "\n")
        
        # 각 영상을 토픽별로 분류
        video_topics = defaultdict(list)
        
        for video in data:
            topic_scores = self.classify_video(video)
            
            # 가장 높은 점수의 토픽에 할당 (복수 토픽 가능)
            for topic_name, score_data in sorted(topic_scores.items(), 
                                                  key=lambda x: x[1]['score'], 
                                                  reverse=True):
                video_topics[topic_name].append({
                    'video': video,
                    'score': score_data['score'],
                    'matched_keywords': score_data['matched_keywords']
                })
        
        return video_topics
    
    def print_topic_summary(self, video_topics):
        """토픽별 요약 출력"""
        print("\n" + "="*80)
        print("📈 토픽별 영상 수")
        print("="*80 + "\n")
        
        # 토픽별 영상 수로 정렬
        sorted_topics = sorted(video_topics.items(), 
                              key=lambda x: len(x[1]), 
                              reverse=True)
        
        for idx, (topic_name, videos) in enumerate(sorted_topics, 1):
            print(f"{idx:2d}. {topic_name}: {len(videos)}개 영상")
        
        print("\n" + "="*80)
        print("🔍 토픽별 상세 내용")
        print("="*80)
        
        for topic_name, videos in sorted_topics:
            if not videos:
                continue
                
            print(f"\n{'─'*80}")
            print(f"{topic_name} ({len(videos)}개 영상)")
            print(f"{'─'*80}\n")
            
            # 영상을 점수순으로 정렬
            sorted_videos = sorted(videos, key=lambda x: x['score'], reverse=True)
            
            # 상위 10개만 출력
            for idx, item in enumerate(sorted_videos[:10], 1):
                video = item['video']
                score = item['score']
                keywords = item['matched_keywords']
                
                print(f"{idx}. 🎬 {video['video_title']}")
                print(f"   채널: {video['channel_name']}")
                print(f"   URL: {video['video_url']}")
                
                try:
                    view_count = int(video['view_count'])
                    print(f"   조회수: {view_count:,}")
                except:
                    print(f"   조회수: {video['view_count']}")
                
                print(f"   관련도: {score}점")
                print(f"   매칭 키워드: {', '.join(keywords[:5])}")
                
                # 대표 세그먼트 1개만 출력
                if video['keyword_segments']:
                    seg_info = video['keyword_segments'][0]
                    seg = seg_info['segment']
                    timestamp = seg.get('start', 0)
                    minutes = int(timestamp // 60)
                    seconds = int(timestamp % 60)
                    text = seg.get('text', '')[:80]
                    print(f"   예시: [{minutes:02d}:{seconds:02d}] {text}...")
                
                print()
            
            if len(sorted_videos) > 10:
                print(f"   ... 외 {len(sorted_videos) - 10}개 영상\n")
    
    def export_topic_report(self, video_topics, output_file='smartphone_topics_report.txt'):
        """토픽별 리포트 저장"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("📊 스마트폰 관련 콘텐츠 토픽 분석 리포트\n")
            f.write("="*80 + "\n\n")
            
            # 토픽별 영상 수로 정렬
            sorted_topics = sorted(video_topics.items(), 
                                  key=lambda x: len(x[1]), 
                                  reverse=True)
            
            for topic_name, videos in sorted_topics:
                if not videos:
                    continue
                
                f.write(f"\n{'='*80}\n")
                f.write(f"{topic_name} ({len(videos)}개 영상)\n")
                f.write(f"{'='*80}\n\n")
                
                # 영상을 점수순으로 정렬
                sorted_videos = sorted(videos, key=lambda x: x['score'], reverse=True)
                
                for idx, item in enumerate(sorted_videos, 1):
                    video = item['video']
                    score = item['score']
                    keywords = item['matched_keywords']
                    
                    f.write(f"[{idx}] {video['video_title']}\n")
                    f.write(f"{'─'*80}\n")
                    f.write(f"채널: {video['channel_name']}\n")
                    f.write(f"URL: {video['video_url']}\n")
                    
                    try:
                        view_count = int(video['view_count'])
                        f.write(f"조회수: {view_count:,}\n")
                    except:
                        f.write(f"조회수: {video['view_count']}\n")
                    
                    f.write(f"관련도 점수: {score}\n")
                    f.write(f"매칭 키워드: {', '.join(keywords)}\n")
                    f.write(f"\n관련 내용:\n")
                    
                    # 세그먼트 출력 (최대 3개)
                    for seg_info in video['keyword_segments'][:3]:
                        seg = seg_info['segment']
                        timestamp = seg.get('start', 0)
                        minutes = int(timestamp // 60)
                        seconds = int(timestamp % 60)
                        text = seg.get('text', '')
                        
                        f.write(f"  [{minutes:02d}:{seconds:02d}] {text}\n")
                    
                    f.write("\n")
        
        print(f"📄 토픽 리포트 저장: {output_file}\n")
    
    def get_topic_statistics(self, video_topics):
        """토픽 통계 정보"""
        print("\n" + "="*80)
        print("📊 토픽 통계")
        print("="*80 + "\n")
        
        total_videos = sum(len(videos) for videos in video_topics.values())
        
        # 채널별 주요 토픽 분석
        channel_topics = defaultdict(lambda: defaultdict(int))
        
        for topic_name, videos in video_topics.items():
            for item in videos:
                channel = item['video']['channel_name']
                channel_topics[channel][topic_name] += 1
        
        print("📺 채널별 주요 토픽:\n")
        
        for channel, topics in sorted(channel_topics.items(), 
                                      key=lambda x: sum(x[1].values()), 
                                      reverse=True)[:10]:
            print(f"{channel}:")
            sorted_channel_topics = sorted(topics.items(), 
                                          key=lambda x: x[1], 
                                          reverse=True)
            for topic, count in sorted_channel_topics[:3]:
                print(f"  - {topic}: {count}개")
            print()


if __name__ == "__main__":
    analyzer = SmartphoneTopicAnalyzer()
    
    # 토픽 분석 실행
    video_topics = analyzer.analyze_topics()
    
    # 결과 출력
    analyzer.print_topic_summary(video_topics)
    
    # 통계 정보
    analyzer.get_topic_statistics(video_topics)
    
    # 리포트 저장
    analyzer.export_topic_report(video_topics)
    
    print("\n" + "="*80)
    print("✅ 토픽 분석 완료!")
    print("="*80)
    print(f"📄 상세 리포트: smartphone_topics_report.txt")
    print("="*80 + "\n")

