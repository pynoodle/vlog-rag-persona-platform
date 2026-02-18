from googleapiclient.discovery import build
import json
import re

class VideoToChannelConverter:
    def __init__(self, api_key):
        """
        비디오 ID를 채널 ID로 변환하는 클래스
        
        Args:
            api_key: YouTube Data API v3 키
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def parse_video_ids(self, video_id_string):
        """
        문자열에서 유효한 비디오 ID들을 추출
        YouTube 비디오 ID는 11자 길이의 영숫자와 - _ 문자로 구성
        
        Args:
            video_id_string: 비디오 ID가 포함된 문자열
            
        Returns:
            list: 추출된 비디오 ID 리스트
        """
        # YouTube 비디오 ID 패턴: 11자 길이의 영숫자, -, _
        pattern = r'[A-Za-z0-9_-]{11}'
        video_ids = re.findall(pattern, video_id_string)
        
        # 중복 제거
        video_ids = list(dict.fromkeys(video_ids))
        
        return video_ids
    
    def get_channel_from_video(self, video_id):
        """
        단일 비디오 ID에서 채널 ID와 정보 가져오기
        
        Args:
            video_id: YouTube 비디오 ID (11자)
            
        Returns:
            dict: 비디오와 채널 정보
        """
        print(f"처리 중: {video_id}")
        
        try:
            response = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()
            
            if response.get('items'):
                video = response['items'][0]
                snippet = video['snippet']
                stats = video.get('statistics', {})
                
                result = {
                    'video_id': video_id,
                    'video_url': f'https://www.youtube.com/watch?v={video_id}',
                    'video_title': snippet['title'],
                    'channel_id': snippet['channelId'],
                    'channel_title': snippet['channelTitle'],
                    'published_at': snippet['publishedAt'],
                    'view_count': stats.get('viewCount', 'N/A'),
                    'like_count': stats.get('likeCount', 'N/A'),
                    'comment_count': stats.get('commentCount', 'N/A'),
                    'success': True
                }
                
                print(f"  ✅ 채널: {snippet['channelTitle']} (ID: {snippet['channelId']})")
                return result
            else:
                print(f"  ❌ 비디오를 찾을 수 없음")
                return {
                    'video_id': video_id,
                    'video_url': f'https://www.youtube.com/watch?v={video_id}',
                    'channel_id': None,
                    'success': False,
                    'error': '비디오를 찾을 수 없습니다'
                }
                
        except Exception as e:
            print(f"  ❌ 에러: {e}")
            return {
                'video_id': video_id,
                'video_url': f'https://www.youtube.com/watch?v={video_id}',
                'channel_id': None,
                'success': False,
                'error': str(e)
            }
    
    def batch_get_channels_from_videos(self, video_ids):
        """
        여러 비디오 ID에서 채널 정보 가져오기 (배치 처리)
        최대 50개씩 한 번에 요청
        
        Args:
            video_ids: 비디오 ID 리스트
            
        Returns:
            list: 결과 딕셔너리 리스트
        """
        results = []
        batch_size = 50
        
        print(f"\n{'='*60}")
        print(f"총 {len(video_ids)}개 비디오 처리 시작")
        print(f"{'='*60}\n")
        
        for i in range(0, len(video_ids), batch_size):
            batch = video_ids[i:i+batch_size]
            print(f"배치 {i//batch_size + 1}: {len(batch)}개 처리 중...")
            
            try:
                response = self.youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(batch)
                ).execute()
                
                # 성공한 비디오들
                found_video_ids = set()
                for video in response.get('items', []):
                    video_id = video['id']
                    found_video_ids.add(video_id)
                    snippet = video['snippet']
                    stats = video.get('statistics', {})
                    
                    result = {
                        'video_id': video_id,
                        'video_url': f'https://www.youtube.com/watch?v={video_id}',
                        'video_title': snippet['title'],
                        'channel_id': snippet['channelId'],
                        'channel_title': snippet['channelTitle'],
                        'published_at': snippet['publishedAt'],
                        'view_count': stats.get('viewCount', 'N/A'),
                        'like_count': stats.get('likeCount', 'N/A'),
                        'comment_count': stats.get('commentCount', 'N/A'),
                        'success': True
                    }
                    results.append(result)
                
                # 찾지 못한 비디오들
                for video_id in batch:
                    if video_id not in found_video_ids:
                        results.append({
                            'video_id': video_id,
                            'video_url': f'https://www.youtube.com/watch?v={video_id}',
                            'channel_id': None,
                            'success': False,
                            'error': '비디오를 찾을 수 없습니다'
                        })
                        
            except Exception as e:
                print(f"  배치 처리 에러: {e}")
                for video_id in batch:
                    results.append({
                        'video_id': video_id,
                        'video_url': f'https://www.youtube.com/watch?v={video_id}',
                        'channel_id': None,
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    def print_results(self, results):
        """결과를 보기 좋게 출력"""
        print(f"\n{'='*60}")
        print("변환 결과")
        print(f"{'='*60}\n")
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        # 채널별로 그룹화
        channels = {}
        for result in successful:
            channel_id = result['channel_id']
            if channel_id not in channels:
                channels[channel_id] = {
                    'channel_id': channel_id,
                    'channel_title': result['channel_title'],
                    'videos': []
                }
            channels[channel_id]['videos'].append(result)
        
        print(f"✅ 성공: {len(successful)}개 비디오")
        print(f"\n발견된 채널: {len(channels)}개\n")
        
        for idx, (channel_id, data) in enumerate(channels.items(), 1):
            print(f"{idx}. 채널: {data['channel_title']}")
            print(f"   채널 ID: {channel_id}")
            print(f"   비디오 수: {len(data['videos'])}개")
            print(f"   비디오 목록:")
            for video in data['videos'][:5]:  # 최대 5개만 표시
                print(f"     - {video['video_title'][:50]}... ({video['video_id']})")
            if len(data['videos']) > 5:
                print(f"     ... 외 {len(data['videos']) - 5}개")
            print()
        
        if failed:
            print(f"\n❌ 실패: {len(failed)}개")
            for result in failed[:10]:  # 최대 10개만 표시
                print(f"  - {result['video_id']}: {result.get('error', '알 수 없는 오류')}")
            if len(failed) > 10:
                print(f"  ... 외 {len(failed) - 10}개")
        
        print(f"\n{'='*60}")
    
    def get_channel_id_list(self, results):
        """중복 제거한 채널 ID 리스트 반환"""
        channel_ids = list(set([r['channel_id'] for r in results if r['success']]))
        return channel_ids
    
    def get_channel_summary(self, results):
        """채널별 통계 요약"""
        channels = {}
        for result in results:
            if result['success']:
                channel_id = result['channel_id']
                if channel_id not in channels:
                    channels[channel_id] = {
                        'channel_id': channel_id,
                        'channel_title': result['channel_title'],
                        'video_count': 0,
                        'video_ids': []
                    }
                channels[channel_id]['video_count'] += 1
                channels[channel_id]['video_ids'].append(result['video_id'])
        
        return list(channels.values())
    
    def save_to_json(self, results, filename='video_to_channel.json'):
        """결과를 JSON 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"📁 결과 저장 완료: {filename}")


if __name__ == "__main__":
    # YouTube API 키
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    
    # 비디오 ID 문자열 (여기에 붙여넣기)
    video_id_string = """
    NcG3QyyOhckCtdkEgP3t6UfpYdhiVW1dYSCqn8K55ZeYSp7FWUygyZItVZepbtajCMKzTXQZhHprg4UblHJ42BlELF27jJWBsqMWDi1wwXzHosHJeXT8CSGUoL67TV6nN5DsWWWrKdXjnPgL0tNjoDAmaEv6KMq1uSSvEQuMT1b_0dvQ1ShHuPq1_sg0H-OzxuEuFoeUcDKKAdAv473fFcR1AEPAvKJWZxsOpMAczfFhmA0XoQxlTpX1VXQ2EX5FHiNbWJq0sXWZvGQ6-XYd_kkmjsdl90mfvtASeI8sYly55hZDEn-oizJwivvFg3kfFkjpraHEqYJNzAWC0phNcQ4Ez5utQjnYd0GNYhsY5Yg8XkP5WUl56wuojNKyzP0g8neSOIvhvTV8ar5Iqg7MUUMbT6EBqhb-lQLGNmEv5x-SsyhCcdUC-L6kDdvyv0oPAWgn68zAfg1Lbg_WTdcg2QLnUXlc-XGvNf3or9S5rFrh3WkenOTJd0T7vIY0RfwHOD4ZwEc6vlzd7wbQ#NAME?IH6IrNIHXloxaExOtDOI7Ixb9rW7J3K4YBwhzcZS8hMYri0QE1hEeV8iUlLTcVAMycp1g-cuj29w0D6h52ZUpDrsXUOpUND3A_cZuBpgr5fxsQ0EvZgNBGXbYul3grSd3nW4xlds9ULWJUMoPcWcoZY1hQ3iKO1uEh0NMzhn-9Ae-ff8FlDedWGcmYYCoWY1uOZqOY4daMx0bpaSI0xWPJEab4f4RUgr91XUeeEPkudV0R_bGUPMoIhFmLkTUdtpg84txYJYS3p3R49OlNsIf43Ie4n8yYKzgKAybQljY2tN7U6zjiMkcJojpGB_On4FxdMy5Pfsdotrp3Rfezho04P6mqrhcbUAK-mLpuzNp7I7Y0lda-40f0OerGQewZioQNLczPtnizdUGgmDrXMTYDAebXlL__FQa8u7LwDeMXU1IbRswXMGQvuEVEJccdPmH50lAiAsAmVj0AXCTkP43zvS8npleg5mlRrc3Tah5FrvANosvzBFiNhwgM6qu8ba6v9CY6y0d08Pzq_MKoMbMjJ3lQs6WNOQg10OOgOMCJ8edGb3sNOXWB9Nc2y0xq2vLTAippo2h1NsU47vbExqdLEd_0WHEvHTDFEKpvvEqLzQEBc4R5QS-DA8o4c5DoCNsDr9ADwfwYDuYUFFEgeQIDJ4Eiv-wYM0FdMzf2iaxAlwW6Wo8DqzITl368OV9w-M
    """
    
    # 또는 리스트로 직접 입력
    # video_ids = ['dQw4w9WgXcQ', 'jNQXAC9IVRw', 'xxxxxx']
    
    if YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY_HERE":
        print("❌ 에러: YouTube API 키를 입력해주세요!")
        exit(1)
    
    # 변환기 실행
    converter = VideoToChannelConverter(YOUTUBE_API_KEY)
    
    # 문자열에서 비디오 ID 추출
    video_ids = converter.parse_video_ids(video_id_string)
    print(f"추출된 비디오 ID: {len(video_ids)}개")
    print(f"예시: {video_ids[:5]}")
    
    if not video_ids:
        print("\n❌ 유효한 비디오 ID를 찾을 수 없습니다.")
        print("비디오 ID는 11자 길이여야 합니다.")
        print("예: dQw4w9WgXcQ")
        exit(1)
    
    # 배치 처리로 채널 ID 가져오기
    results = converter.batch_get_channels_from_videos(video_ids)
    
    # 결과 출력
    converter.print_results(results)
    
    # 채널 ID만 추출
    channel_ids = converter.get_channel_id_list(results)
    
    print("\n📋 채널 ID 리스트 (중복 제거):")
    print("-" * 60)
    for idx, channel_id in enumerate(channel_ids, 1):
        print(f"{idx}. {channel_id}")
    
    print(f"\n채널 ID 배열:")
    print(channel_ids)
    
    # 채널별 요약
    channel_summary = converter.get_channel_summary(results)
    print(f"\n📊 채널별 요약:")
    print("-" * 60)
    for channel in channel_summary:
        print(f"{channel['channel_title']}: {channel['video_count']}개 비디오")
    
    # JSON 저장
    converter.save_to_json(results)
    
    print("\n💡 이 채널 ID들을 스크래퍼에 바로 사용할 수 있습니다!")