# -*- coding: utf-8 -*-
import os
import sys
import json
import glob
import re
from datetime import datetime

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class SmartphoneContentFilter:
    def __init__(self, data_dir='youtube_data'):
        self.data_dir = data_dir
        
        # 스마트폰 관련 키워드 (영어)
        self.keywords_en = [
            'smartphone', 'smart phone', 'iphone', 'galaxy', 'android',
            'imessage', 'facetime', 'airdrop', 'ios', 'siri',
            'phone', 'mobile', 'cell phone', 'samsung', 'pixel',
            'app store', 'google play', 'whatsapp', 'instagram app',
            'text message', 'messaging', 'selfie', 'camera phone',
            'screen time', 'notification', 'charging', 'battery',
            'touchscreen', 'wireless', '5g', 'wifi', 'bluetooth',
            'apple watch', 'airpods', 'earbuds', 'case', 'screen protector'
        ]
        
        # 스마트폰 관련 키워드 (한국어 - STT로 한글 변환된 경우)
        self.keywords_ko = [
            '스마트폰', '스마트 폰', '아이폰', '갤럭시', '안드로이드',
            '아이메시지', '페이스타임', '에어드롭', '아이오에스', '시리',
            '휴대폰', '핸드폰', '휴대전화', '삼성', '픽셀',
            '앱스토어', '앱 스토어', '구글플레이', '왓츠앱', '인스타그램',
            '문자', '메시지', '셀카', '카메라', '배터리',
            '충전', '알림', '터치스크린', '무선', '와이파이', '블루투스',
            '애플워치', '에어팟', '이어폰', '케이스', '액정보호필름'
        ]
        
        self.all_keywords = self.keywords_en + self.keywords_ko
    
    def search_in_text(self, text):
        """텍스트에서 키워드 찾기"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.all_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))  # 중복 제거
    
    def get_context(self, segments, keyword_indices, context_range=2):
        """키워드 주변 문맥 가져오기"""
        results = []
        
        for idx in keyword_indices:
            start_idx = max(0, idx - context_range)
            end_idx = min(len(segments), idx + context_range + 1)
            
            context_segments = segments[start_idx:end_idx]
            
            # 타임스탬프와 텍스트 조합
            context_text = []
            for seg in context_segments:
                timestamp = seg.get('start', 0)
                text = seg.get('text', '')
                context_text.append({
                    'timestamp': timestamp,
                    'text': text.strip()
                })
            
            results.append(context_text)
        
        return results
    
    def filter_videos(self):
        """스마트폰 관련 영상 필터링"""
        
        if not os.path.exists(self.data_dir):
            print(f"❌ {self.data_dir} 폴더가 없습니다.")
            return []
        
        print("\n" + "="*80)
        print("📱 스마트폰 관련 콘텐츠 필터링 중...")
        print("="*80 + "\n")
        
        filtered_results = []
        total_videos = 0
        
        # 모든 채널 폴더 순회
        channel_dirs = [d for d in os.listdir(self.data_dir) 
                       if os.path.isdir(os.path.join(self.data_dir, d))]
        
        for channel_id in channel_dirs:
            channel_path = os.path.join(self.data_dir, channel_id)
            
            # 채널 정보 읽기
            channel_info_path = os.path.join(channel_path, 'channel_info.json')
            channel_name = channel_id
            
            if os.path.exists(channel_info_path):
                try:
                    with open(channel_info_path, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        channel_name = info.get('channel_title', channel_id)
                except:
                    pass
            
            # 영상 JSON 파일들 읽기
            json_files = glob.glob(os.path.join(channel_path, '*.json'))
            
            for json_file in json_files:
                if 'channel_info.json' in json_file:
                    continue
                
                total_videos += 1
                
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        video_data = json.load(f)
                    
                    metadata = video_data.get('metadata', {})
                    transcript = video_data.get('transcript', [])
                    
                    if not transcript:
                        continue
                    
                    # 전체 텍스트에서 키워드 검색
                    video_title = metadata.get('title', '')
                    video_description = metadata.get('description', '')
                    
                    # 제목과 설명에서 키워드 찾기
                    title_keywords = self.search_in_text(video_title)
                    desc_keywords = self.search_in_text(video_description)
                    
                    # 전사본에서 키워드 찾기
                    keyword_segments = []
                    for idx, segment in enumerate(transcript):
                        text = segment.get('text', '')
                        keywords = self.search_in_text(text)
                        
                        if keywords:
                            keyword_segments.append({
                                'index': idx,
                                'segment': segment,
                                'keywords': keywords
                            })
                    
                    # 스마트폰 관련 내용이 있으면 결과에 추가
                    if title_keywords or desc_keywords or keyword_segments:
                        all_found_keywords = list(set(
                            title_keywords + desc_keywords + 
                            [kw for seg in keyword_segments for kw in seg['keywords']]
                        ))
                        
                        filtered_results.append({
                            'channel_name': channel_name,
                            'channel_id': channel_id,
                            'video_id': metadata.get('video_id', ''),
                            'video_title': video_title,
                            'video_url': metadata.get('video_url', ''),
                            'view_count': metadata.get('view_count', 0),
                            'published_at': metadata.get('published_at', ''),
                            'found_keywords': all_found_keywords,
                            'keyword_segments': keyword_segments,
                            'transcript_type': video_data.get('transcript_type', 'unknown')
                        })
                
                except Exception as e:
                    print(f"⚠️  에러 ({json_file}): {e}")
                    continue
        
        print(f"✅ 전체 {total_videos}개 영상 중 {len(filtered_results)}개 영상에서 스마트폰 관련 내용 발견!\n")
        
        return filtered_results
    
    def save_results(self, results, output_file='smartphone_filtered_results.json'):
        """결과를 JSON 파일로 저장"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"💾 결과 저장: {output_file}")
    
    def print_summary(self, results):
        """결과 요약 출력"""
        if not results:
            print("❌ 스마트폰 관련 내용을 찾을 수 없습니다.")
            return
        
        print("\n" + "="*80)
        print(f"📊 스마트폰 관련 영상 요약 (총 {len(results)}개)")
        print("="*80 + "\n")
        
        # 채널별로 그룹화
        by_channel = {}
        for result in results:
            channel = result['channel_name']
            if channel not in by_channel:
                by_channel[channel] = []
            by_channel[channel].append(result)
        
        # 채널별 출력
        for idx, (channel, videos) in enumerate(sorted(by_channel.items(), 
                                                       key=lambda x: len(x[1]), 
                                                       reverse=True), 1):
            print(f"{idx}. 📺 {channel}: {len(videos)}개 영상")
            
            for video in videos:
                print(f"\n   🎬 {video['video_title']}")
                print(f"      URL: {video['video_url']}")
                
                # 조회수를 정수로 변환 시도
                try:
                    view_count = int(video['view_count'])
                    print(f"      조회수: {view_count:,}")
                except (ValueError, TypeError):
                    print(f"      조회수: {video['view_count']}")
                print(f"      발견된 키워드: {', '.join(video['found_keywords'][:10])}")
                
                # 일부 키워드 세그먼트 출력 (최대 3개)
                if video['keyword_segments']:
                    print(f"      관련 내용 위치: {len(video['keyword_segments'])}곳")
                    
                    for seg_info in video['keyword_segments'][:3]:
                        seg = seg_info['segment']
                        timestamp = seg.get('start', 0)
                        minutes = int(timestamp // 60)
                        seconds = int(timestamp % 60)
                        text = seg.get('text', '')[:100]
                        
                        print(f"         [{minutes:02d}:{seconds:02d}] {text}...")
                
                print()
            
            print("-" * 80 + "\n")
    
    def export_detailed_report(self, results, output_file='smartphone_detailed_report.txt'):
        """상세 리포트 텍스트 파일로 출력"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("📱 스마트폰 관련 콘텐츠 상세 리포트\n")
            f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"총 {len(results)}개 영상\n")
            f.write("="*80 + "\n\n")
            
            for idx, result in enumerate(results, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"[{idx}] {result['video_title']}\n")
                f.write(f"{'='*80}\n")
                f.write(f"채널: {result['channel_name']}\n")
                f.write(f"URL: {result['video_url']}\n")
                
                # 조회수를 정수로 변환 시도
                try:
                    view_count = int(result['view_count'])
                    f.write(f"조회수: {view_count:,}\n")
                except (ValueError, TypeError):
                    f.write(f"조회수: {result['view_count']}\n")
                f.write(f"발행일: {result['published_at']}\n")
                f.write(f"전사 타입: {result['transcript_type']}\n")
                f.write(f"발견된 키워드: {', '.join(result['found_keywords'])}\n")
                f.write(f"\n{'─'*80}\n")
                f.write(f"스마트폰 관련 내용 ({len(result['keyword_segments'])}곳):\n")
                f.write(f"{'─'*80}\n\n")
                
                for seg_info in result['keyword_segments']:
                    seg = seg_info['segment']
                    keywords = seg_info['keywords']
                    timestamp = seg.get('start', 0)
                    minutes = int(timestamp // 60)
                    seconds = int(timestamp % 60)
                    text = seg.get('text', '')
                    
                    f.write(f"[{minutes:02d}:{seconds:02d}] (키워드: {', '.join(keywords)})\n")
                    f.write(f"{text}\n\n")
                
                f.write("\n")
        
        print(f"📄 상세 리포트 저장: {output_file}\n")


if __name__ == "__main__":
    filter_tool = SmartphoneContentFilter()
    
    # 필터링 실행
    results = filter_tool.filter_videos()
    
    # 결과 출력
    filter_tool.print_summary(results)
    
    # 결과 저장
    if results:
        filter_tool.save_results(results)
        filter_tool.export_detailed_report(results)
        
        print("\n" + "="*80)
        print("✅ 필터링 완료!")
        print("="*80)
        print(f"📊 요약: {len(results)}개 영상에서 스마트폰 관련 내용 발견")
        print(f"💾 JSON 결과: smartphone_filtered_results.json")
        print(f"📄 상세 리포트: smartphone_detailed_report.txt")
        print("="*80 + "\n")
    else:
        print("\n스마트폰 관련 내용을 찾을 수 없습니다.\n")

