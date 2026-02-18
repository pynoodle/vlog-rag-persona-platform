# -*- coding: utf-8 -*-
import os
import sys
import json
from collections import Counter, defaultdict
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class RealTopicExtractor:
    def __init__(self, input_file='smartphone_filtered_results.json'):
        self.input_file = input_file
    
    def load_data(self):
        """데이터 로드"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_context_patterns(self, data):
        """실제 텍스트에서 스마트폰 관련 맥락 추출"""
        
        # 스마트폰 관련 키워드와 함께 자주 언급되는 단어들 찾기
        context_words = []
        phone_mentions = []
        
        for video in data:
            for seg_info in video['keyword_segments']:
                seg = seg_info['segment']
                text = seg.get('text', '').lower()
                
                # 스마트폰 관련 내용 추출
                phone_mentions.append({
                    'channel': video['channel_name'],
                    'video_title': video['video_title'],
                    'text': seg.get('text', ''),
                    'timestamp': seg.get('start', 0),
                    'keywords': seg_info['keywords']
                })
                
                # 텍스트를 단어로 분리
                words = re.findall(r'\b\w+\b', text)
                context_words.extend(words)
        
        return phone_mentions, context_words
    
    def analyze_actual_topics(self, phone_mentions):
        """실제 언급된 내용을 기반으로 토픽 분류"""
        
        print("\n" + "="*80)
        print("📊 실제 텍스트 기반 토픽 분석")
        print("="*80 + "\n")
        
        # 실제 언급된 내용 패턴 분석
        topics = defaultdict(list)
        
        for mention in phone_mentions:
            text = mention['text'].lower()
            
            # 실제 텍스트에서 토픽 추출 (지어내지 않음!)
            matched = False
            
            # 1. iPhone 신제품/모델 언급
            if any(word in text for word in ['iphone 16', 'iphone 15', 'iphone 14', 'iphone 13', 
                                              'iphone 11', 'iphone xr', 'new phone', 'unboxing']):
                topics['📦 iPhone 신제품/언박싱'].append(mention)
                matched = True
            
            # 2. 폰 케이스/액세서리
            if any(word in text for word in ['phone case', 'case', 'casetify', 'accessories', 
                                              'screen protector', 'airpods', 'earbuds']):
                topics['🎨 폰 케이스 & 액세서리'].append(mention)
                matched = True
            
            # 3. 배터리/충전
            if any(word in text for word in ['battery', 'charging', 'charger', 'power', '충전', '배터리']):
                topics['🔋 배터리 & 충전'].append(mention)
                matched = True
            
            # 4. 스크린 타임/폰 중독
            if any(word in text for word in ['screen time', 'phone control', 'phone addiction',
                                              'scrolling', 'notification', 'mindful']):
                topics['📱 스크린 타임 & 디지털 웰빙'].append(mention)
                matched = True
            
            # 5. 사진/영상 촬영
            if any(word in text for word in ['camera', 'filming', 'selfie', 'photo', 'recording',
                                              '카메라', '셀카']):
                topics['📸 사진 & 영상 촬영'].append(mention)
                matched = True
            
            # 6. 앱 사용/추천
            if any(word in text for word in ['app', 'ios', 'android', 'app store', 'widget',
                                              'tiktok', 'instagram']):
                topics['📲 앱 & 소프트웨어'].append(mention)
                matched = True
            
            # 7. 소통/메시징
            if any(word in text for word in ['facetime', 'imessage', 'text message', 'messaging',
                                              'call', 'whatsapp', '문자', '메시지']):
                topics['💬 메시징 & 통화'].append(mention)
                matched = True
            
            # 8. 폰으로 작업/비즈니스
            if any(word in text for word in ['business', 'work', 'editing', 'content creator',
                                              'youtube', 'vlog']):
                topics['💼 콘텐츠 제작 & 비즈니스'].append(mention)
                matched = True
            
            # 9. Android/다른 브랜드 폰
            if any(word in text for word in ['android', 'oppo', 'vivo', 'samsung', 'galaxy',
                                              'tecno', 'pixel']):
                topics['🤖 Android & 다른 브랜드'].append(mention)
                matched = True
            
            # 10. 폰 전환/설정
            if any(word in text for word in ['switched phone', 'new phone', 'setup', 'transfer',
                                              'getting everything over']):
                topics['🔄 폰 전환 & 설정'].append(mention)
                matched = True
        
        return topics
    
    def print_real_topic_summary(self, topics):
        """실제 데이터 기반 토픽 요약"""
        
        print(f"\n{'='*80}")
        print(f"📈 실제 언급된 토픽별 분포")
        print(f"{'='*80}\n")
        
        sorted_topics = sorted(topics.items(), key=lambda x: len(x[1]), reverse=True)
        
        for idx, (topic_name, mentions) in enumerate(sorted_topics, 1):
            print(f"{idx:2d}. {topic_name}: {len(mentions)}회 언급")
        
        print(f"\n{'='*80}")
        print(f"📝 토픽별 실제 언급 내용 (상위 5개)")
        print(f"{'='*80}\n")
        
        for topic_name, mentions in sorted_topics[:10]:
            print(f"\n{'─'*80}")
            print(f"{topic_name} ({len(mentions)}회 언급)")
            print(f"{'─'*80}\n")
            
            # 대표 예시 5개
            for idx, mention in enumerate(mentions[:5], 1):
                timestamp = mention['timestamp']
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                
                print(f"{idx}. 📺 {mention['channel']}")
                print(f"   🎬 {mention['video_title']}")
                print(f"   ⏱️ [{minutes:02d}:{seconds:02d}]")
                print(f"   💬 \"{mention['text'][:100]}...\"")
                print()
            
            if len(mentions) > 5:
                print(f"   ... 외 {len(mentions) - 5}개 언급\n")
    
    def export_topic_examples(self, topics, output_file='real_smartphone_topics.txt'):
        """실제 언급 내용을 파일로 저장"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("📱 스마트폰 관련 실제 언급 내용 분석\n")
            f.write("="*80 + "\n\n")
            
            sorted_topics = sorted(topics.items(), key=lambda x: len(x[1]), reverse=True)
            
            for topic_name, mentions in sorted_topics:
                f.write(f"\n{'='*80}\n")
                f.write(f"{topic_name} ({len(mentions)}회 언급)\n")
                f.write(f"{'='*80}\n\n")
                
                for idx, mention in enumerate(mentions, 1):
                    timestamp = mention['timestamp']
                    minutes = int(timestamp // 60)
                    seconds = int(timestamp % 60)
                    
                    f.write(f"[{idx}] 채널: {mention['channel']}\n")
                    f.write(f"    영상: {mention['video_title']}\n")
                    f.write(f"    시간: [{minutes:02d}:{seconds:02d}]\n")
                    f.write(f"    내용: {mention['text']}\n")
                    f.write(f"    키워드: {', '.join(mention['keywords'])}\n\n")
        
        print(f"💾 실제 언급 내용 저장: {output_file}\n")
    
    def get_topic_statistics(self, data, topics):
        """토픽 통계"""
        
        print(f"\n{'='*80}")
        print(f"📊 통계 요약")
        print(f"{'='*80}\n")
        
        total_videos = len(data)
        total_mentions = sum(len(mentions) for mentions in topics.values())
        
        print(f"📹 스마트폰 관련 영상: {total_videos}개")
        print(f"💬 총 언급 횟수: {total_mentions}회")
        print(f"📈 평균: 영상당 {total_mentions/total_videos:.1f}회 언급\n")
        
        # 채널별 주요 토픽
        channel_topics = defaultdict(lambda: defaultdict(int))
        
        for topic_name, mentions in topics.items():
            for mention in mentions:
                channel = mention['channel']
                channel_topics[channel][topic_name] += 1
        
        print(f"{'─'*80}")
        print(f"📺 채널별 주요 관심 토픽 (상위 10개):")
        print(f"{'─'*80}\n")
        
        for channel, channel_topic_counts in sorted(channel_topics.items(), 
                                                     key=lambda x: sum(x[1].values()),
                                                     reverse=True)[:10]:
            total_count = sum(channel_topic_counts.values())
            print(f"{channel}:")
            
            sorted_channel_topics = sorted(channel_topic_counts.items(),
                                          key=lambda x: x[1],
                                          reverse=True)[:3]
            
            for topic, count in sorted_channel_topics:
                percent = count / total_count * 100
                print(f"  - {topic}: {count}회 ({percent:.0f}%)")
            print()


if __name__ == "__main__":
    extractor = RealTopicExtractor()
    
    # 데이터 로드
    data = extractor.load_data()
    
    print(f"\n📱 스마트폰 관련 영상: {len(data)}개")
    
    # 실제 언급 내용 추출
    phone_mentions, context_words = extractor.extract_context_patterns(data)
    
    print(f"💬 스마트폰 관련 언급 횟수: {len(phone_mentions)}회\n")
    
    # 토픽 분석
    topics = extractor.analyze_actual_topics(phone_mentions)
    
    # 결과 출력
    extractor.print_real_topic_summary(topics)
    
    # 통계
    extractor.get_topic_statistics(data, topics)
    
    # 파일 저장
    extractor.export_topic_examples(topics)
    
    print("\n" + "="*80)
    print("✅ 실제 텍스트 기반 토픽 분석 완료!")
    print("="*80)
    print("📄 상세 내용: real_smartphone_topics.txt")
    print("="*80 + "\n")

