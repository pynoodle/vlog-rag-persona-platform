# -*- coding: utf-8 -*-
"""
일상 & 라이프스타일 콘텐츠 액티비티 분석
브이로거들의 라이프스타일 유형별 상세 분석
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
            continue
    
    return all_videos

# 라이프스타일 액티비티 키워드 정의 (전역 변수)
ACTIVITY_KEYWORDS = {
        '☀️ 모닝 루틴': [
            'morning routine', 'wake up', 'morning', 'breakfast', 'skincare routine',
            'get ready', 'grwm', 'morning coffee', 'alarm', 'sunrise',
            '아침', '모닝', '루틴', '기상'
        ],
        '🛏️ 나이트 루틴': [
            'night routine', 'evening routine', 'bedtime', 'sleep', 'night skincare',
            'wind down', 'before bed', 'nighttime', 'shower before bed',
            '밤', '취침', '저녁 루틴', '잠'
        ],
        '🧹 청소 & 정리': [
            'clean', 'cleaning', 'organize', 'declutter', 'tidy', 'laundry',
            'vacuum', 'dust', 'deep clean', 'organization', 'reset',
            '청소', '정리', '정돈', '빨래'
        ],
        '🛍️ 쇼핑 & 하울': [
            'shopping', 'haul', 'shop', 'mall', 'store', 'target', 'amazon',
            'unboxing', 'buy', 'purchase', 'shopping spree',
            '쇼핑', '하울', '언박싱', '구매'
        ],
        '🍳 요리 & 식사': [
            'cook', 'cooking', 'meal prep', 'recipe', 'baking', 'dinner',
            'lunch', 'eat', 'kitchen', 'food prep',
            '요리', '식사', '밥', '먹'
        ],
        '💅 셀프케어 & 뷰티': [
            'self care', 'skincare', 'face mask', 'spa', 'pamper', 'relax',
            'bath', 'nail', 'manicure', 'hair care', 'massage',
            '셀프케어', '스킨케어', '마스크팩', '휴식'
        ],
        '💪 운동 & 피트니스': [
            'workout', 'exercise', 'gym', 'yoga', 'pilates', 'run', 'running',
            'fitness', 'training', 'walk', 'walking',
            '운동', '헬스', '요가', '산책'
        ],
        '📖 독서 & 저널링': [
            'journal', 'journaling', 'diary', 'read', 'reading', 'book',
            'write', 'writing', 'planner', 'note',
            '일기', '독서', '책', '저널'
        ],
        '🎨 취미 & 창작': [
            'draw', 'drawing', 'paint', 'painting', 'craft', 'diy', 'hobby',
            'creative', 'art', 'create', 'making',
            '그림', '만들기', '취미', '창작'
        ],
        '👗 옷차림 & 스타일링': [
            'outfit', 'get dressed', 'closet', 'wardrobe', 'style', 'fashion',
            'clothes', 'what to wear', 'try on',
            '옷', '코디', '스타일링'
        ],
        '☕ 카페 & 외출': [
            'cafe', 'coffee shop', 'starbucks', 'brunch', 'go out', 'errands',
            'run errands', 'grocery', 'grocery shopping',
            '카페', '외출', '장보기'
        ],
        '🏡 홈 데코 & 인테리어': [
            'decor', 'decoration', 'decorate', 'room makeover', 'interior',
            'furniture', 'home decor', 'room tour', 'organize room',
            '인테리어', '꾸미기', '방꾸미기'
        ],
        '👯 친구 & 사교': [
            'hang out', 'meet friends', 'catch up', 'sleepover', 'party',
            'social', 'gathering', 'friends', 'meet up',
            '친구', '만남', '놀기'
        ],
        '🎬 콘텐츠 작업': [
            'filming', 'edit video', 'editing', 'content creation', 'photoshoot',
            'upload', 'thumbnail', 'film', 'record',
            '촬영', '편집', '영상 작업'
        ],
        '🧘 마인드풀니스 & 휴식': [
            'meditation', 'mindfulness', 'relax', 'chill', 'rest', 'slow',
            'peaceful', 'calm', 'unwind', 'me time',
            '명상', '휴식', '힐링', '여유'
        ],
        '📱 디지털 & 테크': [
            'phone', 'screen time', 'social media', 'scroll', 'apps',
            'instagram', 'tiktok', 'youtube', 'digital',
            '폰', '핸드폰', '스마트폰'
        ]
}

def categorize_lifestyle_activities(videos):
    """라이프스타일 액티비티별로 분류"""
    
    # 액티비티별 영상 분류
    activity_videos = defaultdict(list)
    activity_keyword_counts = defaultdict(Counter)
    activity_examples = defaultdict(list)
    
    for video in videos:
        if not video.get('has_text'):
            continue
        
        text = video['full_text'].lower()
        
        for activity, keywords in ACTIVITY_KEYWORDS.items():
            # 키워드 매칭
            matched_keywords = []
            matched_phrases = []
            
            for kw in keywords:
                if kw.lower() in text:
                    matched_keywords.append(kw)
                    # 해당 키워드가 포함된 문장 찾기
                    sentences = text.split('.')
                    for sentence in sentences:
                        if kw.lower() in sentence and len(sentence.strip()) > 20:
                            matched_phrases.append(sentence.strip()[:200])
                            break
            
            if matched_keywords:
                activity_videos[activity].append(video)
                
                # 키워드별 카운트
                for kw in matched_keywords:
                    count = text.count(kw.lower())
                    activity_keyword_counts[activity][kw] += count
                
                # 예시 문장 저장 (최대 3개)
                if len(activity_examples[activity]) < 5:
                    activity_examples[activity].extend([
                        {
                            'channel': video['metadata']['channel_title'],
                            'title': video['metadata']['title'],
                            'phrase': phrase,
                            'keyword': matched_keywords[0],
                            'views': video['metadata'].get('view_count', '0')
                        }
                        for phrase in matched_phrases[:1]
                    ])
    
    return activity_videos, activity_keyword_counts, activity_examples

def find_specific_activities(videos):
    """구체적인 액티비티 패턴 찾기"""
    
    specific_patterns = {
        '🌅 아침 활동': [
            r'wake up at \d+', r'morning walk', r'breakfast at', r'coffee first',
            r'start the day', r'meditation', r'morning workout'
        ],
        '🍽️ 식사 준비': [
            r'meal prep', r'cook breakfast', r'make lunch', r'dinner recipe',
            r'food prep', r'batch cooking'
        ],
        '🚿 셀프케어': [
            r'shower', r'bath', r'face mask', r'skin care', r'hair wash',
            r'self care sunday', r'pamper myself'
        ],
        '🏠 집안일': [
            r'laundry', r'dishes', r'vacuum', r'deep clean', r'organize closet',
            r'declutter', r'tidy up'
        ],
        '💼 일 & 업무': [
            r'work from home', r'meeting', r'office', r'emails', r'project',
            r'deadline', r'conference call'
        ],
        '🎮 여가 활동': [
            r'watch movie', r'netflix', r'gaming', r'scroll', r'social media',
            r'browse', r'chill time'
        ]
    }
    
    activity_matches = defaultdict(list)
    
    for video in videos:
        if not video.get('has_text'):
            continue
        
        text = video['full_text'].lower()
        
        for activity, patterns in specific_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    activity_matches[activity].append({
                        'video': video,
                        'matches': matches,
                        'pattern': pattern
                    })
    
    return activity_matches

def main():
    print("="*80)
    print("🏠 일상 & 라이프스타일 콘텐츠 상세 분석")
    print("="*80)
    print()
    
    # 데이터 로드
    print("데이터 로딩 중...")
    all_videos = load_all_videos()
    
    # 일상 & 라이프스타일 토픽 키워드
    lifestyle_keywords = [
        'vlog', 'day', 'morning', 'routine', 'life', 'home', 'room', 'organize',
        'clean', 'decoration', 'apartment', 'house', 'bedroom', 'daily',
        '일상', '브이로그', '루틴', '집', '방', '정리'
    ]
    
    # 라이프스타일 영상 필터링
    lifestyle_videos = []
    for video in all_videos:
        if not video.get('has_text'):
            continue
        
        text = video['full_text'].lower()
        if any(kw.lower() in text for kw in lifestyle_keywords):
            lifestyle_videos.append(video)
    
    print(f"✓ 일상 & 라이프스타일 영상: {len(lifestyle_videos)}개")
    print()
    
    # 액티비티 분석
    print("액티비티 분류 중...")
    activity_videos, activity_keyword_counts, activity_examples = categorize_lifestyle_activities(lifestyle_videos)
    
    # 결과 저장
    output = []
    output.append("="*80)
    output.append("🏠 일상 & 라이프스타일 콘텐츠 - 액티비티 상세 분석")
    output.append("="*80)
    output.append("")
    output.append(f"분석 대상: {len(lifestyle_videos)}개 영상")
    output.append(f"총 채널: {len(set(v['channel_id'] for v in lifestyle_videos))}개")
    output.append("")
    
    # 액티비티별 정렬 (영상 수 기준)
    sorted_activities = sorted(activity_videos.items(), key=lambda x: len(x[1]), reverse=True)
    
    output.append("="*80)
    output.append("📋 라이프스타일 유형별 영상 수")
    output.append("="*80)
    output.append("")
    
    for activity, vids in sorted_activities:
        percentage = len(vids) / len(lifestyle_videos) * 100
        output.append(f"{activity}: {len(vids)}개 ({percentage:.1f}%)")
    
    output.append("")
    
    # 각 액티비티 상세 분석
    for activity, vids in sorted_activities:
        output.append("")
        output.append("="*80)
        output.append(f"{activity} ({len(vids)}개 영상)")
        output.append("="*80)
        output.append("")
        
        # 주요 키워드
        keyword_counts = activity_keyword_counts[activity]
        top_keywords = keyword_counts.most_common(15)
        
        output.append("🔑 주요 키워드 (언급 횟수):")
        for kw, count in top_keywords:
            output.append(f"  - {kw}: {count}회")
        output.append("")
        
        # 채널별 분포
        channel_counts = Counter([v['metadata']['channel_title'] for v in vids])
        output.append("📺 이 액티비티를 많이 하는 채널 TOP 10:")
        for channel, count in channel_counts.most_common(10):
            output.append(f"  - {channel}: {count}개 영상")
        output.append("")
        
        # 인기 영상
        sorted_vids = sorted(vids, key=lambda x: int(x['metadata'].get('view_count', '0').replace(',', '')), reverse=True)
        
        output.append("⭐ 조회수 높은 영상 TOP 5:")
        for idx, video in enumerate(sorted_vids[:5], 1):
            meta = video['metadata']
            output.append(f"  [{idx}] {meta['title']}")
            output.append(f"      채널: {meta['channel_title']}")
            output.append(f"      조회수: {meta.get('view_count', 'N/A')}")
            output.append("")
        
        # 실제 언급 예시
        if activity in activity_examples and activity_examples[activity]:
            output.append("💬 실제 콘텐츠 예시:")
            for idx, example in enumerate(activity_examples[activity][:5], 1):
                output.append(f"  [{idx}] 채널: {example['channel']}")
                output.append(f"      영상: {example['title']}")
                output.append(f"      조회수: {example['views']}")
                output.append(f"      키워드: {example['keyword']}")
                output.append(f"      내용: \"{example['phrase'][:150]}...\"")
                output.append("")
    
    # 채널별 라이프스타일 분석
    output.append("")
    output.append("="*80)
    output.append("📺 채널별 라이프스타일 특징")
    output.append("="*80)
    output.append("")
    
    # 채널별로 어떤 액티비티를 많이 하는지 분석
    channel_activities = defaultdict(lambda: defaultdict(int))
    
    for activity, vids in activity_videos.items():
        for video in vids:
            channel = video['metadata']['channel_title']
            channel_activities[channel][activity] += 1
    
    # 채널별 정렬 (총 영상 수 기준)
    sorted_channels = sorted(
        channel_activities.items(),
        key=lambda x: sum(x[1].values()),
        reverse=True
    )
    
    for channel, activities in sorted_channels[:15]:
        output.append(f"\n📺 {channel}")
        output.append(f"   총 라이프스타일 영상: {sum(activities.values())}개")
        output.append("   주요 액티비티:")
        
        sorted_acts = sorted(activities.items(), key=lambda x: x[1], reverse=True)
        for act, count in sorted_acts[:5]:
            output.append(f"     - {act}: {count}개")
    
    output.append("")
    
    # 조합 패턴 분석
    output.append("")
    output.append("="*80)
    output.append("🔄 자주 함께 나오는 액티비티 조합")
    output.append("="*80)
    output.append("")
    
    # 한 영상에 여러 액티비티가 있는 경우 찾기
    multi_activity_videos = []
    for video in lifestyle_videos:
        video_activities = []
        text = video['full_text'].lower()
        
        for activity, keywords in ACTIVITY_KEYWORDS.items():
            if any(kw.lower() in text for kw in keywords):
                video_activities.append(activity)
        
        if len(video_activities) >= 3:
            multi_activity_videos.append({
                'video': video,
                'activities': video_activities,
                'count': len(video_activities)
            })
    
    # 조합 빈도 계산
    combination_counts = Counter()
    for item in multi_activity_videos:
        activities = tuple(sorted(item['activities']))
        if len(activities) >= 3:
            combination_counts[activities] += 1
    
    output.append("자주 함께 등장하는 액티비티 (3개 이상):")
    for idx, (combo, count) in enumerate(combination_counts.most_common(10), 1):
        output.append(f"  [{idx}] 조합 ({count}개 영상):")
        for act in combo:
            output.append(f"      - {act}")
        output.append("")
    
    # 파일로 저장
    output_text = '\n'.join(output)
    
    with open('lifestyle_activities_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    # 화면에도 출력
    print(output_text)
    
    print()
    print("="*80)
    print("✓ 분석 완료!")
    print("✓ 결과 저장: lifestyle_activities_analysis.txt")
    print("="*80)

if __name__ == "__main__":
    main()

