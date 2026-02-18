# -*- coding: utf-8 -*-
import os
import sys
import json
import glob

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def summarize_collected_data(data_dir='youtube_data'):
    """수집된 데이터 요약"""
    
    if not os.path.exists(data_dir):
        print(f"❌ {data_dir} 폴더가 없습니다.")
        return
    
    # 채널 폴더 목록
    channel_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    
    print("\n" + "="*70)
    print("📊 수집 데이터 요약")
    print("="*70 + "\n")
    
    total_videos = 0
    channels_with_data = []
    
    for channel_id in sorted(channel_dirs):
        channel_path = os.path.join(data_dir, channel_id)
        
        # channel_info.json 읽기
        channel_info_path = os.path.join(channel_path, 'channel_info.json')
        channel_name = channel_id
        
        if os.path.exists(channel_info_path):
            try:
                with open(channel_info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    channel_name = info.get('channel_title', channel_id)
            except:
                pass
        
        # 영상 JSON 파일 수 세기 (channel_info.json 제외)
        json_files = glob.glob(os.path.join(channel_path, '*.json'))
        video_count = len([f for f in json_files if 'channel_info.json' not in f])
        
        if video_count > 0:
            channels_with_data.append({
                'name': channel_name,
                'id': channel_id,
                'count': video_count
            })
            total_videos += video_count
    
    # 영상 수 많은 순으로 정렬
    channels_with_data.sort(key=lambda x: x['count'], reverse=True)
    
    # 출력
    for idx, channel in enumerate(channels_with_data, 1):
        print(f"{idx:2d}. {channel['name']:<40} {channel['count']:3d}개 영상")
    
    print("\n" + "="*70)
    print(f"✅ 총 {len(channels_with_data)}개 채널에서 {total_videos}개 영상 수집 완료!")
    print("="*70 + "\n")
    
    # 추가 통계
    if channels_with_data:
        avg_videos = total_videos / len(channels_with_data)
        print(f"📈 평균: 채널당 {avg_videos:.1f}개 영상")
        print(f"📊 최대: {channels_with_data[0]['name']} ({channels_with_data[0]['count']}개)")
        print(f"📊 최소: {channels_with_data[-1]['name']} ({channels_with_data[-1]['count']}개)\n")

if __name__ == "__main__":
    summarize_collected_data()

