# -*- coding: utf-8 -*-
"""
전체 STT 데이터 토픽 분석
모든 수집된 영상의 텍스트를 분석하여 주요 토픽 추출
"""

import json
import os
import glob
from collections import Counter, defaultdict
import re
import sys

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def load_all_videos():
    """모든 채널의 영상 데이터 로드"""
    all_videos = []
    
    for json_file in glob.glob('youtube_data/*/*.json'):
        if 'channel_info' in json_file:
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                video = json.load(f)
                
                # 채널 정보 추가
                channel_id = os.path.basename(os.path.dirname(json_file))
                video['channel_id'] = channel_id
                
                # 전체 텍스트 생성
                full_text = ""
                if video.get('transcript'):
                    full_text = ' '.join([item['text'] for item in video['transcript']])
                elif video.get('stt_text'):
                    full_text = video['stt_text']
                
                video['full_text'] = full_text
                video['has_text'] = bool(full_text.strip())
                
                all_videos.append(video)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    return all_videos

def extract_keywords(text, min_length=3):
    """텍스트에서 주요 키워드 추출 (빈도 기반)"""
    # 소문자 변환 및 단어 분리
    words = re.findall(r'\b\w+\b', text.lower())
    
    # 불용어 제거
    stopwords = {
        'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are', 'was', 'were',
        'to', 'in', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
        'be', 'been', 'being', 'am', 'so', 'just', 'like', 'know', 'get', 'go', 'going',
        'really', 'very', 'much', 'can', 'but', 'or', 'if', 'because', 'when', 'where',
        'what', 'who', 'how', 'all', 'there', 'some', 'out', 'than', 'other', 'now',
        'make', 'made', 'want', 'see', 'look', 'use', 'think', 'also', 'back', 'way',
        'even', 'well', 'need', 'thing', 'things', 'time', 'got', 'gonna', 'yeah', 'okay',
        '가', '이', '그', '저', '것', '수', '등', '및', '더', '매우', '정말', '진짜', '좀',
        '한', '또', '그리고', '하지만', '그래서', '왜냐하면', '때문에', '있다', '없다', '하다'
    }
    
    # 최소 길이 이상, 불용어 제외
    filtered_words = [w for w in words if len(w) >= min_length and w not in stopwords]
    
    return filtered_words

def categorize_topics(videos):
    """토픽별로 영상 분류"""
    
    # 주요 토픽 키워드 정의
    topic_keywords = {
        '🎨 뷰티 & 메이크업': [
            'makeup', 'beauty', 'skincare', 'hair', 'nail', 'lipstick', 'foundation', 
            'mascara', 'eyeshadow', 'blush', 'concealer', 'primer', 'serum', 'moisturizer',
            '메이크업', '화장', '뷰티', '스킨케어', '헤어', '네일', '립스틱'
        ],
        '👗 패션 & 쇼핑': [
            'outfit', 'fashion', 'clothes', 'shopping', 'haul', 'dress', 'style', 'wear',
            'jeans', 'shirt', 'shoes', 'bag', 'accessory', 'jewelry', 'wardrobe',
            '옷', '패션', '쇼핑', '스타일', '가방', '신발', '액세서리'
        ],
        '🍳 음식 & 요리': [
            'food', 'cook', 'recipe', 'eat', 'meal', 'dinner', 'lunch', 'breakfast',
            'kitchen', 'coffee', 'drink', 'restaurant', 'dessert', 'ingredient',
            '음식', '요리', '레시피', '먹', '식사', '커피', '카페'
        ],
        '💪 건강 & 피트니스': [
            'workout', 'fitness', 'exercise', 'gym', 'health', 'diet', 'weight', 'yoga',
            'cardio', 'muscle', 'training', 'routine', 'body',
            '운동', '헬스', '다이어트', '건강', '요가', '피트니스'
        ],
        '📚 학교 & 공부': [
            'school', 'study', 'student', 'class', 'exam', 'homework', 'notebook', 'pencil',
            'college', 'university', 'grade', 'test', 'learn', 'education',
            '학교', '공부', '시험', '수업', '노트', '필기', '대학'
        ],
        '🏠 일상 & 라이프스타일': [
            'vlog', 'day', 'morning', 'routine', 'life', 'home', 'room', 'organize',
            'clean', 'decoration', 'apartment', 'house', 'bedroom', 'daily',
            '일상', '브이로그', '루틴', '집', '방', '정리'
        ],
        '✈️ 여행 & 휴가': [
            'travel', 'trip', 'vacation', 'hotel', 'flight', 'airport', 'tour', 'visit',
            'beach', 'city', 'country', 'destination', 'adventure',
            '여행', '휴가', '호텔', '비행기', '공항'
        ],
        '💼 비즈니스 & 창업': [
            'business', 'work', 'office', 'entrepreneur', 'launch', 'product', 'brand',
            'marketing', 'sales', 'company', 'startup', 'client', 'meeting',
            '비즈니스', '사업', '회사', '브랜드', '제품', '런칭'
        ],
        '📱 스마트폰 & IT': [
            'smartphone', 'iphone', 'android', 'phone', 'app', 'camera', 'video', 'photo',
            'battery', 'charger', 'case', 'screen', 'tablet', 'ipad', 'laptop', 'computer',
            '스마트폰', '아이폰', '폰', '앱', '카메라', '배터리', '케이스'
        ],
        '🎥 콘텐츠 제작': [
            'film', 'filming', 'camera', 'edit', 'editing', 'youtube', 'content', 'creator',
            'vlog', 'thumbnail', 'upload', 'video', 'shoot', 'lighting',
            '촬영', '편집', '영상', '유튜브', '콘텐츠', '크리에이터'
        ],
        '💑 관계 & 친구': [
            'friend', 'boyfriend', 'girlfriend', 'relationship', 'date', 'family', 'mom',
            'dad', 'sister', 'brother', 'partner', 'love', 'friendship',
            '친구', '남친', '여친', '가족', '엄마', '아빠', '사랑'
        ],
        '🌱 환경 & 사회': [
            'climate', 'environment', 'sustainability', 'activism', 'change', 'future',
            'planet', 'carbon', 'emissions', 'crisis', 'protest',
            '환경', '기후', '지속가능', '변화', '미래'
        ],
        '🎬 엔터테인먼트': [
            'movie', 'music', 'show', 'concert', 'festival', 'celebrity', 'entertainment',
            'song', 'album', 'performance', 'event', 'party',
            '영화', '음악', '공연', '페스티벌', '파티'
        ]
    }
    
    # 토픽별 영상 분류
    topic_videos = defaultdict(list)
    topic_keyword_counts = defaultdict(Counter)
    
    for video in videos:
        if not video.get('has_text'):
            continue
        
        text = video['full_text'].lower()
        video_topics = []
        
        for topic, keywords in topic_keywords.items():
            # 키워드 매칭
            matched_keywords = [kw for kw in keywords if kw.lower() in text]
            
            if matched_keywords:
                video_topics.append(topic)
                topic_videos[topic].append(video)
                
                # 키워드별 카운트
                for kw in matched_keywords:
                    count = text.count(kw.lower())
                    topic_keyword_counts[topic][kw] += count
        
        video['topics'] = video_topics
    
    return topic_videos, topic_keyword_counts

def analyze_word_frequency(videos, top_n=100):
    """전체 텍스트에서 단어 빈도 분석"""
    all_text = " ".join([v['full_text'] for v in videos if v.get('has_text')])
    
    words = extract_keywords(all_text)
    word_freq = Counter(words)
    
    return word_freq.most_common(top_n)

def main():
    print("="*80)
    print("📊 전체 STT 데이터 토픽 분석")
    print("="*80)
    print()
    
    # 데이터 로드
    print("데이터 로딩 중...")
    videos = load_all_videos()
    text_videos = [v for v in videos if v.get('has_text')]
    
    print(f"✓ 총 {len(videos)}개 영상 로드")
    print(f"✓ 텍스트 있는 영상: {len(text_videos)}개")
    print()
    
    # 토픽 분류
    print("토픽 분류 중...")
    topic_videos, topic_keyword_counts = categorize_topics(videos)
    
    # 결과 저장할 문자열
    output = []
    output.append("="*80)
    output.append("📊 전체 STT 데이터 토픽 분석 결과")
    output.append("="*80)
    output.append("")
    output.append(f"총 영상: {len(videos)}개")
    output.append(f"텍스트 있음: {len(text_videos)}개")
    output.append(f"분석 채널: {len(set(v['channel_id'] for v in videos))}개")
    output.append("")
    
    # 토픽별 정렬 (영상 수 기준)
    sorted_topics = sorted(topic_videos.items(), key=lambda x: len(x[1]), reverse=True)
    
    output.append("="*80)
    output.append("📋 토픽별 영상 수 요약")
    output.append("="*80)
    output.append("")
    
    for topic, vids in sorted_topics:
        output.append(f"{topic}: {len(vids)}개 영상")
    
    output.append("")
    
    # 각 토픽 상세 분석
    for topic, vids in sorted_topics:
        output.append("")
        output.append("="*80)
        output.append(f"{topic} ({len(vids)}개 영상)")
        output.append("="*80)
        output.append("")
        
        # 주요 키워드 (빈도순)
        keyword_counts = topic_keyword_counts[topic]
        top_keywords = keyword_counts.most_common(20)
        
        output.append("🔑 주요 키워드 (언급 횟수):")
        for kw, count in top_keywords:
            output.append(f"  - {kw}: {count}회")
        output.append("")
        
        # 채널별 영상 수
        channel_counts = Counter([v['metadata']['channel_title'] for v in vids])
        output.append("📺 채널별 분포:")
        for channel, count in channel_counts.most_common(10):
            output.append(f"  - {channel}: {count}개")
        output.append("")
        
        # 대표 영상 (조회수 높은 순)
        sorted_vids = sorted(vids, key=lambda x: x['metadata'].get('view_count', '0').replace(',', ''), reverse=True)
        
        output.append("⭐ 인기 영상 TOP 5:")
        for idx, video in enumerate(sorted_vids[:5], 1):
            meta = video['metadata']
            output.append(f"  [{idx}] {meta['title']}")
            output.append(f"      채널: {meta['channel_title']}")
            output.append(f"      조회수: {meta.get('view_count', 'N/A')}")
            output.append(f"      URL: {meta.get('video_url', 'N/A')}")
            output.append("")
    
    # 전체 단어 빈도 분석
    output.append("")
    output.append("="*80)
    output.append("📈 전체 단어 빈도 분석 (TOP 100)")
    output.append("="*80)
    output.append("")
    
    word_freq = analyze_word_frequency(videos, top_n=100)
    
    for idx, (word, count) in enumerate(word_freq, 1):
        output.append(f"{idx:3d}. {word}: {count:,}회")
    
    output.append("")
    
    # 파일로 저장
    output_text = '\n'.join(output)
    
    with open('all_topics_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    # 화면에도 출력
    print(output_text)
    
    print()
    print("="*80)
    print("✓ 분석 완료!")
    print("✓ 결과 저장: all_topics_analysis.txt")
    print("="*80)

if __name__ == "__main__":
    main()

