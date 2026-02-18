# -*- coding: utf-8 -*-
import os
import sys
import json
import glob
from datetime import datetime
from collections import defaultdict, Counter
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class VideoDataAnalyzer:
    """자막/STT 데이터를 자연어로 분석하는 대화형 인터페이스"""
    
    def __init__(self, data_dir='youtube_data'):
        self.data_dir = data_dir
        self.videos_db = []
        self.load_database()
    
    def load_database(self):
        """모든 영상 데이터를 메모리에 로드"""
        print("\n🔄 데이터베이스 로딩 중...")
        
        if not os.path.exists(self.data_dir):
            print(f"❌ {self.data_dir} 폴더가 없습니다.")
            return
        
        channel_dirs = [d for d in os.listdir(self.data_dir) 
                       if os.path.isdir(os.path.join(self.data_dir, d))]
        
        for channel_id in channel_dirs:
            channel_path = os.path.join(self.data_dir, channel_id)
            
            # 채널 정보
            channel_info_path = os.path.join(channel_path, 'channel_info.json')
            channel_name = channel_id
            
            if os.path.exists(channel_info_path):
                try:
                    with open(channel_info_path, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        channel_name = info.get('channel_title', channel_id)
                except:
                    pass
            
            # 영상 데이터 로드
            json_files = glob.glob(os.path.join(channel_path, '*.json'))
            
            for json_file in json_files:
                if 'channel_info.json' in json_file:
                    continue
                
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        video_data = json.load(f)
                    
                    # 데이터베이스에 추가
                    video_data['channel_name'] = channel_name
                    video_data['channel_id'] = channel_id
                    
                    # 전체 텍스트 생성 (검색용)
                    full_text = ""
                    if video_data.get('transcript'):
                        full_text = " ".join([seg.get('text', '') for seg in video_data['transcript']])
                    
                    video_data['full_text'] = full_text
                    video_data['full_text_lower'] = full_text.lower()
                    
                    self.videos_db.append(video_data)
                    
                except Exception as e:
                    continue
        
        # 자막/STT가 있는 것만 필터링
        self.videos_with_text = [v for v in self.videos_db if v.get('full_text')]
        
        print(f"✅ 총 {len(self.videos_db)}개 영상 로드 완료!")
        print(f"   자막/STT 있음: {len(self.videos_with_text)}개\n")
    
    def search_keyword(self, keyword):
        """키워드로 영상 검색"""
        keyword_lower = keyword.lower()
        results = []
        
        for video in self.videos_with_text:
            if keyword_lower in video['full_text_lower']:
                # 키워드가 포함된 세그먼트 찾기
                matching_segments = []
                for seg in video['transcript']:
                    if keyword_lower in seg.get('text', '').lower():
                        matching_segments.append(seg)
                
                results.append({
                    'video': video,
                    'match_count': len(matching_segments),
                    'matching_segments': matching_segments
                })
        
        # 매칭 횟수로 정렬
        results.sort(key=lambda x: x['match_count'], reverse=True)
        return results
    
    def search_multiple_keywords(self, keywords, mode='OR'):
        """여러 키워드로 검색 (OR/AND)"""
        if mode == 'OR':
            results = set()
            for keyword in keywords:
                keyword_results = self.search_keyword(keyword)
                for r in keyword_results:
                    results.add(r['video']['metadata']['video_id'])
            
            # 결과 재구성
            return [r for r in self.videos_with_text if r['metadata']['video_id'] in results]
        
        elif mode == 'AND':
            results = self.videos_with_text.copy()
            for keyword in keywords:
                keyword_lower = keyword.lower()
                results = [v for v in results if keyword_lower in v['full_text_lower']]
            return results
    
    def filter_by_channel(self, channel_name_part):
        """채널명으로 필터링"""
        results = []
        for video in self.videos_with_text:
            if channel_name_part.lower() in video['channel_name'].lower():
                results.append(video)
        return results
    
    def get_top_videos_by_views(self, limit=10, keyword=None):
        """조회수 상위 영상"""
        videos = self.videos_with_text.copy()
        
        if keyword:
            videos = [v for v in videos if keyword.lower() in v['full_text_lower']]
        
        videos.sort(key=lambda x: int(x['metadata'].get('view_count', 0)), reverse=True)
        return videos[:limit]
    
    def analyze_sentiment_patterns(self, keyword):
        """키워드 주변의 감성/맥락 분석"""
        results = self.search_keyword(keyword)
        
        positive_words = ['love', 'great', 'best', 'amazing', 'perfect', 'favorite', 
                         'good', 'beautiful', 'awesome', '좋', '최고', '사랑']
        negative_words = ['hate', 'bad', 'worst', 'terrible', 'problem', 'issue',
                         'annoying', 'frustrating', '싫', '안좋', '최악']
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        examples = {'positive': [], 'negative': [], 'neutral': []}
        
        for result in results:
            for seg in result['matching_segments']:
                text = seg.get('text', '').lower()
                
                is_positive = any(word in text for word in positive_words)
                is_negative = any(word in text for word in negative_words)
                
                if is_positive and not is_negative:
                    positive_count += 1
                    if len(examples['positive']) < 3:
                        examples['positive'].append({
                            'text': seg.get('text', ''),
                            'video_title': result['video']['metadata']['title'],
                            'channel': result['video']['channel_name']
                        })
                elif is_negative and not is_positive:
                    negative_count += 1
                    if len(examples['negative']) < 3:
                        examples['negative'].append({
                            'text': seg.get('text', ''),
                            'video_title': result['video']['metadata']['title'],
                            'channel': result['video']['channel_name']
                        })
                else:
                    neutral_count += 1
                    if len(examples['neutral']) < 3:
                        examples['neutral'].append({
                            'text': seg.get('text', ''),
                            'video_title': result['video']['metadata']['title'],
                            'channel': result['video']['channel_name']
                        })
        
        return {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'examples': examples
        }
    
    def get_statistics(self):
        """전체 통계"""
        return {
            'total_videos': len(self.videos_db),
            'videos_with_text': len(self.videos_with_text),
            'total_channels': len(set(v['channel_id'] for v in self.videos_db)),
            'avg_transcript_length': sum(len(v.get('full_text', '')) for v in self.videos_with_text) / len(self.videos_with_text) if self.videos_with_text else 0
        }
    
    def interactive_query(self):
        """대화형 쿼리 인터페이스"""
        
        print("\n" + "="*80)
        print("💬 YouTube 영상 데이터 분석 챗봇")
        print("="*80 + "\n")
        
        # 통계 정보
        stats = self.get_statistics()
        print(f"📊 로드된 데이터:")
        print(f"   - 총 영상: {stats['total_videos']}개")
        print(f"   - 자막/STT 있음: {stats['videos_with_text']}개")
        print(f"   - 채널 수: {stats['total_channels']}개")
        print(f"   - 평균 텍스트 길이: {stats['avg_transcript_length']:.0f}자\n")
        
        print("💡 사용 가능한 명령어:")
        print("   1. 검색 <키워드>              - 키워드가 포함된 영상 검색")
        print("   2. 다중검색 <키워드1,키워드2>  - 여러 키워드 검색 (OR)")
        print("   3. 모두검색 <키워드1,키워드2>  - 모든 키워드 포함 검색 (AND)")
        print("   4. 채널 <채널명>              - 특정 채널 영상만 검색")
        print("   5. 인기영상 <키워드>          - 키워드 관련 인기 영상 Top 10")
        print("   6. 감성분석 <키워드>          - 키워드에 대한 긍정/부정 분석")
        print("   7. 통계                       - 전체 통계 정보")
        print("   8. 도움말                     - 명령어 도움말")
        print("   9. 종료                       - 프로그램 종료\n")
        
        print("="*80)
        
        while True:
            try:
                user_input = input("\n💬 명령어를 입력하세요: ").strip()
                
                if not user_input:
                    continue
                
                # 명령어 파싱
                parts = user_input.split(maxsplit=1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                
                if command in ['종료', 'exit', 'quit', 'q']:
                    print("\n👋 프로그램을 종료합니다.\n")
                    break
                
                elif command in ['검색', 'search']:
                    if not args:
                        print("❌ 키워드를 입력하세요. 예: 검색 아이폰")
                        continue
                    
                    self.handle_search(args)
                
                elif command in ['다중검색', 'multi']:
                    if not args:
                        print("❌ 키워드를 입력하세요. 예: 다중검색 아이폰,갤럭시")
                        continue
                    
                    keywords = [k.strip() for k in args.split(',')]
                    self.handle_multi_search(keywords, 'OR')
                
                elif command in ['모두검색', 'all']:
                    if not args:
                        print("❌ 키워드를 입력하세요. 예: 모두검색 아이폰,케이스")
                        continue
                    
                    keywords = [k.strip() for k in args.split(',')]
                    self.handle_multi_search(keywords, 'AND')
                
                elif command in ['채널', 'channel']:
                    if not args:
                        print("❌ 채널명을 입력하세요. 예: 채널 emma")
                        continue
                    
                    self.handle_channel_filter(args)
                
                elif command in ['인기영상', 'popular']:
                    self.handle_popular_videos(args if args else None)
                
                elif command in ['감성분석', 'sentiment']:
                    if not args:
                        print("❌ 키워드를 입력하세요. 예: 감성분석 배터리")
                        continue
                    
                    self.handle_sentiment_analysis(args)
                
                elif command in ['통계', 'stats']:
                    self.handle_statistics()
                
                elif command in ['도움말', 'help', '?']:
                    self.show_help()
                
                else:
                    print(f"❌ 알 수 없는 명령어: {command}")
                    print("   '도움말'을 입력하여 사용 가능한 명령어를 확인하세요.")
            
            except KeyboardInterrupt:
                print("\n\n👋 프로그램을 종료합니다.\n")
                break
            except Exception as e:
                print(f"❌ 에러 발생: {e}")
                continue
    
    def handle_search(self, keyword):
        """키워드 검색 처리"""
        print(f"\n🔍 '{keyword}' 검색 중...\n")
        
        results = self.search_keyword(keyword)
        
        if not results:
            print(f"❌ '{keyword}'가 포함된 영상을 찾을 수 없습니다.\n")
            return
        
        print(f"✅ {len(results)}개 영상에서 총 {sum(r['match_count'] for r in results)}회 발견!\n")
        print("="*80)
        
        # 상위 10개만 출력
        for idx, result in enumerate(results[:10], 1):
            video = result['video']
            metadata = video['metadata']
            
            print(f"\n{idx}. 🎬 {metadata['title']}")
            print(f"   📺 {video['channel_name']}")
            print(f"   🔢 {result['match_count']}회 언급")
            
            try:
                view_count = int(metadata['view_count'])
                print(f"   👁️ {view_count:,} 조회수")
            except:
                print(f"   👁️ {metadata['view_count']} 조회수")
            
            print(f"   🔗 {metadata['video_url']}")
            
            # 대표 언급 1개
            if result['matching_segments']:
                seg = result['matching_segments'][0]
                timestamp = seg.get('start', 0)
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                text = seg.get('text', '')[:80]
                print(f"   💬 [{minutes:02d}:{seconds:02d}] \"{text}...\"")
        
        if len(results) > 10:
            print(f"\n... 외 {len(results) - 10}개 영상")
        
        print("\n" + "="*80)
        
        # 리포트 저장 옵션
        save = input("\n💾 결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"search_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            self.save_search_results(results, keyword, filename)
            print(f"✅ 저장 완료: {filename}\n")
    
    def handle_multi_search(self, keywords, mode):
        """다중 키워드 검색"""
        print(f"\n🔍 키워드 검색 ({mode} 모드): {', '.join(keywords)}\n")
        
        results = self.search_multiple_keywords(keywords, mode)
        
        if not results:
            print(f"❌ 조건에 맞는 영상을 찾을 수 없습니다.\n")
            return
        
        print(f"✅ {len(results)}개 영상 발견!\n")
        print("="*80)
        
        for idx, video in enumerate(results[:10], 1):
            metadata = video['metadata']
            
            print(f"\n{idx}. 🎬 {metadata['title']}")
            print(f"   📺 {video['channel_name']}")
            
            try:
                view_count = int(metadata['view_count'])
                print(f"   👁️ {view_count:,} 조회수")
            except:
                print(f"   👁️ {metadata['view_count']} 조회수")
            
            print(f"   🔗 {metadata['video_url']}")
        
        if len(results) > 10:
            print(f"\n... 외 {len(results) - 10}개 영상")
        
        print("\n" + "="*80)
    
    def handle_channel_filter(self, channel_name):
        """채널 필터"""
        print(f"\n📺 '{channel_name}' 채널 검색 중...\n")
        
        results = self.filter_by_channel(channel_name)
        
        if not results:
            print(f"❌ '{channel_name}' 채널을 찾을 수 없습니다.\n")
            return
        
        # 채널별로 그룹화
        by_channel = defaultdict(list)
        for video in results:
            by_channel[video['channel_name']].append(video)
        
        print(f"✅ {len(by_channel)}개 채널, {len(results)}개 영상 발견!\n")
        print("="*80)
        
        for channel, videos in sorted(by_channel.items()):
            print(f"\n📺 {channel}: {len(videos)}개 영상")
            print("─"*80)
            
            for idx, video in enumerate(videos[:5], 1):
                metadata = video['metadata']
                print(f"   {idx}. {metadata['title']}")
                print(f"      🔗 {metadata['video_url']}")
            
            if len(videos) > 5:
                print(f"   ... 외 {len(videos) - 5}개 영상")
        
        print("\n" + "="*80)
    
    def handle_popular_videos(self, keyword):
        """인기 영상 검색"""
        if keyword:
            print(f"\n🔥 '{keyword}' 관련 인기 영상 Top 10\n")
        else:
            print(f"\n🔥 전체 인기 영상 Top 10\n")
        
        videos = self.get_top_videos_by_views(10, keyword)
        
        if not videos:
            print(f"❌ 영상을 찾을 수 없습니다.\n")
            return
        
        print("="*80)
        
        for idx, video in enumerate(videos, 1):
            metadata = video['metadata']
            
            print(f"\n{idx}. 🎬 {metadata['title']}")
            print(f"   📺 {video['channel_name']}")
            
            try:
                view_count = int(metadata['view_count'])
                print(f"   👁️ {view_count:,} 조회수")
            except:
                print(f"   👁️ {metadata['view_count']} 조회수")
            
            print(f"   🔗 {metadata['video_url']}")
        
        print("\n" + "="*80)
    
    def handle_sentiment_analysis(self, keyword):
        """감성 분석"""
        print(f"\n😊 '{keyword}' 감성 분석 중...\n")
        
        sentiment = self.analyze_sentiment_patterns(keyword)
        
        total = sentiment['positive'] + sentiment['negative'] + sentiment['neutral']
        
        if total == 0:
            print(f"❌ '{keyword}'에 대한 언급을 찾을 수 없습니다.\n")
            return
        
        print("="*80)
        print(f"📊 총 {total}개 언급 분석 결과:")
        print("="*80 + "\n")
        
        print(f"😊 긍정적: {sentiment['positive']}회 ({sentiment['positive']/total*100:.1f}%)")
        print(f"😐 중립적: {sentiment['neutral']}회 ({sentiment['neutral']/total*100:.1f}%)")
        print(f"😞 부정적: {sentiment['negative']}회 ({sentiment['negative']/total*100:.1f}%)\n")
        
        # 예시 출력
        for sentiment_type, label, emoji in [('positive', '긍정적', '😊'), 
                                             ('negative', '부정적', '😞')]:
            examples = sentiment['examples'][sentiment_type]
            if examples:
                print(f"{'─'*80}")
                print(f"{emoji} {label} 언급 예시:")
                print(f"{'─'*80}\n")
                
                for ex in examples:
                    print(f"   📺 {ex['channel']}")
                    print(f"   🎬 {ex['video_title']}")
                    print(f"   💬 \"{ex['text'][:100]}...\"")
                    print()
        
        print("="*80)
    
    def handle_statistics(self):
        """통계 출력"""
        stats = self.get_statistics()
        
        print("\n" + "="*80)
        print("📊 전체 통계")
        print("="*80 + "\n")
        
        print(f"📹 총 영상 수: {stats['total_videos']}개")
        print(f"📝 자막/STT 있음: {stats['videos_with_text']}개")
        print(f"📺 채널 수: {stats['total_channels']}개")
        print(f"📏 평균 텍스트 길이: {stats['avg_transcript_length']:.0f}자")
        
        # 채널별 영상 수
        channel_counts = Counter(v['channel_name'] for v in self.videos_with_text)
        
        print(f"\n{'─'*80}")
        print(f"📺 채널별 영상 수 (자막/STT 있음, 상위 10개):")
        print(f"{'─'*80}\n")
        
        for idx, (channel, count) in enumerate(channel_counts.most_common(10), 1):
            print(f"   {idx:2d}. {channel}: {count}개")
        
        print("\n" + "="*80)
    
    def show_help(self):
        """도움말"""
        print("\n" + "="*80)
        print("💡 명령어 도움말")
        print("="*80 + "\n")
        
        help_text = """
📝 기본 검색:
   검색 아이폰          - '아이폰'이 언급된 영상 검색
   검색 battery         - '배터리' 관련 영상 검색
   검색 케이스          - '케이스' 관련 영상 검색

🔍 고급 검색:
   다중검색 아이폰,갤럭시    - 아이폰 OR 갤럭시 언급 (둘 중 하나)
   모두검색 아이폰,케이스    - 아이폰 AND 케이스 (둘 다 언급)
   채널 emma                - Emma 채널의 영상만 검색

🔥 인기/감성 분석:
   인기영상                 - 전체 인기 영상 Top 10
   인기영상 아이폰          - 아이폰 관련 인기 영상
   감성분석 배터리          - 배터리에 대한 긍정/부정 분석

📊 정보:
   통계                     - 전체 통계 정보
   도움말                   - 이 도움말 표시
   종료                     - 프로그램 종료

💡 팁:
   - 영어/한글 모두 검색 가능
   - 검색 결과는 자동으로 파일 저장 가능
   - 대소문자 구분 없음
        """
        print(help_text)
        print("="*80)
    
    def save_search_results(self, results, keyword, filename):
        """검색 결과 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"🔍 '{keyword}' 검색 결과\n")
            f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"총 {len(results)}개 영상, {sum(r['match_count'] for r in results)}회 언급\n")
            f.write("="*80 + "\n\n")
            
            for idx, result in enumerate(results, 1):
                video = result['video']
                metadata = video['metadata']
                
                f.write(f"\n{'='*80}\n")
                f.write(f"[{idx}] {metadata['title']}\n")
                f.write(f"{'='*80}\n")
                f.write(f"채널: {video['channel_name']}\n")
                f.write(f"URL: {metadata['video_url']}\n")
                
                try:
                    view_count = int(metadata['view_count'])
                    f.write(f"조회수: {view_count:,}\n")
                except:
                    f.write(f"조회수: {metadata['view_count']}\n")
                
                f.write(f"언급 횟수: {result['match_count']}회\n")
                f.write(f"\n{'─'*80}\n")
                f.write(f"언급 내용:\n")
                f.write(f"{'─'*80}\n\n")
                
                for seg in result['matching_segments']:
                    timestamp = seg.get('start', 0)
                    minutes = int(timestamp // 60)
                    seconds = int(timestamp % 60)
                    text = seg.get('text', '')
                    
                    f.write(f"[{minutes:02d}:{seconds:02d}] {text}\n\n")


if __name__ == "__main__":
    analyzer = VideoDataAnalyzer()
    analyzer.interactive_query()

