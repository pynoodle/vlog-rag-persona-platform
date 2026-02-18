# -*- coding: utf-8 -*-
import os
import sys
import json
import glob

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def check_transcript_status(data_dir='youtube_data'):
    """자막/STT 수집 현황 확인"""
    
    if not os.path.exists(data_dir):
        print(f"❌ {data_dir} 폴더가 없습니다.")
        return
    
    print("\n" + "="*80)
    print("📊 자막/STT 수집 현황 분석")
    print("="*80 + "\n")
    
    total_videos = 0
    videos_with_transcript = 0
    videos_without_transcript = 0
    
    transcript_types = {
        'subtitle': 0,
        'auto-generated': 0,
        'whisper-stt': 0,
        'none': 0
    }
    
    channels_data = []
    
    # 모든 채널 폴더 순회
    channel_dirs = [d for d in os.listdir(data_dir) 
                   if os.path.isdir(os.path.join(data_dir, d))]
    
    for channel_id in channel_dirs:
        channel_path = os.path.join(data_dir, channel_id)
        
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
        
        # 영상 JSON 파일들 분석
        json_files = glob.glob(os.path.join(channel_path, '*.json'))
        
        channel_total = 0
        channel_with_transcript = 0
        channel_types = {
            'subtitle': 0,
            'auto-generated': 0,
            'whisper-stt': 0,
            'none': 0
        }
        
        for json_file in json_files:
            if 'channel_info.json' in json_file:
                continue
            
            channel_total += 1
            total_videos += 1
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    video_data = json.load(f)
                
                transcript = video_data.get('transcript')
                trans_type = video_data.get('transcript_type')
                
                if transcript and len(transcript) > 0:
                    videos_with_transcript += 1
                    channel_with_transcript += 1
                    
                    if trans_type:
                        channel_types[trans_type] = channel_types.get(trans_type, 0) + 1
                        transcript_types[trans_type] = transcript_types.get(trans_type, 0) + 1
                    else:
                        channel_types['none'] += 1
                        transcript_types['none'] += 1
                else:
                    videos_without_transcript += 1
                    channel_types['none'] += 1
                    transcript_types['none'] += 1
                    
            except Exception as e:
                continue
        
        if channel_total > 0:
            channels_data.append({
                'name': channel_name,
                'id': channel_id,
                'total': channel_total,
                'with_transcript': channel_with_transcript,
                'types': channel_types
            })
    
    # 전체 통계
    print(f"{'='*80}")
    print(f"전체 통계")
    print(f"{'='*80}\n")
    
    print(f"📹 총 영상 수: {total_videos}개")
    print(f"✅ 자막/STT 있음: {videos_with_transcript}개 ({videos_with_transcript/total_videos*100:.1f}%)")
    print(f"❌ 자막/STT 없음: {videos_without_transcript}개 ({videos_without_transcript/total_videos*100:.1f}%)")
    
    print(f"\n{'─'*80}")
    print(f"📝 전사 타입별 분포:")
    print(f"{'─'*80}\n")
    
    print(f"   📄 수동 자막 (subtitle): {transcript_types.get('subtitle', 0)}개")
    print(f"   🤖 자동 생성 자막 (auto-generated): {transcript_types.get('auto-generated', 0)}개")
    print(f"   🎙️ Whisper STT: {transcript_types.get('whisper-stt', 0)}개")
    print(f"   ❌ 없음: {transcript_types.get('none', 0)}개")
    
    # 채널별 상세 정보 (자막 있는 채널만)
    print(f"\n{'='*80}")
    print(f"채널별 자막/STT 수집 현황")
    print(f"{'='*80}\n")
    
    # 자막이 있는 비율로 정렬
    channels_data_sorted = sorted(channels_data, 
                                  key=lambda x: x['with_transcript'], 
                                  reverse=True)
    
    for idx, channel in enumerate(channels_data_sorted[:30], 1):
        if channel['with_transcript'] > 0:
            percent = channel['with_transcript'] / channel['total'] * 100
            print(f"{idx:2d}. {channel['name']:<40} "
                  f"{channel['with_transcript']}/{channel['total']}개 ({percent:.0f}%)")
    
    # 자막이 없는 채널
    channels_no_transcript = [c for c in channels_data if c['with_transcript'] == 0]
    
    if channels_no_transcript:
        print(f"\n{'─'*80}")
        print(f"⚠️ 자막/STT가 하나도 없는 채널: {len(channels_no_transcript)}개")
        print(f"{'─'*80}\n")
        
        for channel in channels_no_transcript[:10]:
            print(f"   - {channel['name']}: {channel['total']}개 영상 (메타데이터만)")
        
        if len(channels_no_transcript) > 10:
            print(f"   ... 외 {len(channels_no_transcript) - 10}개 채널")

if __name__ == "__main__":
    check_transcript_status()

