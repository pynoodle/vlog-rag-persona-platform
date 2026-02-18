from googleapiclient.discovery import build
import json

class YouTubeHandleConverter:
    def __init__(self, api_key):
        """
        YouTube 핸들 변환기 초기화
        
        Args:
            api_key: YouTube Data API v3 키
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def handle_to_channel_id(self, handle):
        """
        단일 핸들을 채널 ID로 변환
        
        Args:
            handle: @로 시작하는 핸들 (예: @kyliejenner) 또는 핸들명만 (예: kyliejenner)
            
        Returns:
            dict: {'handle': str, 'channel_id': str, 'channel_name': str, 'success': bool}
        """
        # @ 제거
        clean_handle = handle.lstrip('@')
        
        print(f"검색 중: @{clean_handle}")
        
        try:
            # forHandle 파라미터로 검색
            response = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                forHandle=clean_handle
            ).execute()
            
            if response.get('items'):
                channel = response['items'][0]
                channel_id = channel['id']
                channel_name = channel['snippet']['title']
                
                result = {
                    'handle': f'@{clean_handle}',
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'subscriber_count': channel['statistics'].get('subscriberCount', 'N/A'),
                    'video_count': channel['statistics'].get('videoCount', 'N/A'),
                    'success': True
                }
                
                print(f"  ✅ 찾음: {channel_name} (ID: {channel_id})")
                return result
            else:
                # forHandle로 못 찾으면 검색 API로 시도
                search_response = self.youtube.search().list(
                    part='snippet',
                    q=clean_handle,
                    type='channel',
                    maxResults=1
                ).execute()
                
                if search_response.get('items'):
                    channel = search_response['items'][0]
                    channel_id = channel['snippet']['channelId']
                    channel_name = channel['snippet']['title']
                    
                    # 통계 정보 추가 조회
                    stats_response = self.youtube.channels().list(
                        part='statistics',
                        id=channel_id
                    ).execute()
                    
                    stats = stats_response['items'][0]['statistics'] if stats_response.get('items') else {}
                    
                    result = {
                        'handle': f'@{clean_handle}',
                        'channel_id': channel_id,
                        'channel_name': channel_name,
                        'subscriber_count': stats.get('subscriberCount', 'N/A'),
                        'video_count': stats.get('videoCount', 'N/A'),
                        'success': True
                    }
                    
                    print(f"  ✅ 찾음 (검색): {channel_name} (ID: {channel_id})")
                    return result
                else:
                    print(f"  ❌ 찾을 수 없음")
                    return {
                        'handle': f'@{clean_handle}',
                        'channel_id': None,
                        'channel_name': None,
                        'subscriber_count': None,
                        'video_count': None,
                        'success': False,
                        'error': '채널을 찾을 수 없습니다'
                    }
                    
        except Exception as e:
            print(f"  ❌ 에러: {e}")
            return {
                'handle': f'@{clean_handle}',
                'channel_id': None,
                'channel_name': None,
                'subscriber_count': None,
                'video_count': None,
                'success': False,
                'error': str(e)
            }
    
    def convert_handles_to_ids(self, handles):
        """
        여러 핸들을 채널 ID로 변환
        
        Args:
            handles: 핸들 리스트 (예: ['@kyliejenner', '@CharlidAmelio'])
            
        Returns:
            list: 변환 결과 딕셔너리 리스트
        """
        print(f"\n{'='*60}")
        print(f"총 {len(handles)}개 핸들 변환 시작")
        print(f"{'='*60}\n")
        
        results = []
        
        for idx, handle in enumerate(handles, 1):
            print(f"[{idx}/{len(handles)}]", end=" ")
            result = self.handle_to_channel_id(handle)
            results.append(result)
        
        return results
    
    def print_results(self, results):
        """결과를 보기 좋게 출력"""
        print(f"\n{'='*60}")
        print("변환 결과")
        print(f"{'='*60}\n")
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if successful:
            print("✅ 성공:")
            for result in successful:
                print(f"\n  핸들: {result['handle']}")
                print(f"  채널명: {result['channel_name']}")
                print(f"  채널 ID: {result['channel_id']}")
                print(f"  구독자: {result['subscriber_count']}")
                print(f"  영상 수: {result['video_count']}")
        
        if failed:
            print(f"\n❌ 실패 ({len(failed)}개):")
            for result in failed:
                print(f"\n  핸들: {result['handle']}")
                print(f"  에러: {result.get('error', '알 수 없는 오류')}")
        
        print(f"\n{'='*60}")
        print(f"총 {len(successful)}개 성공, {len(failed)}개 실패")
        print(f"{'='*60}\n")
    
    def get_channel_id_list(self, results):
        """성공한 결과에서 채널 ID만 추출"""
        return [r['channel_id'] for r in results if r['success']]
    
    def save_to_json(self, results, filename='channel_ids.json'):
        """결과를 JSON 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"📁 결과 저장 완료: {filename}")


if __name__ == "__main__":
    # YouTube API 키 입력
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    
    # 변환할 핸들 리스트
    handles = [
        "@kyliejenner",
        "@CharlidAmelio",
        "@gretathunberg7607",
        "@khabylame",
        "@emmachamberlain",
        "@kaylaitsines",
        "@maddieziegler",
        "@CasJerome",
        "@BretmanRock",
        "@mollymae9879",
        "@BrooklynAndBailey",
        "@JamesCharles",
        "@rickeythompson",
        "@LauuraGab",
        "@trinitymorissette2577",
        "@SarahBaska",
        "@daniellecarolan"

    ]
    
    # API 키 확인
    if YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY_HERE":
        print("❌ 에러: YouTube API 키를 입력해주세요!")
        print("   YOUTUBE_API_KEY 변수를 수정하세요.")
        exit(1)
    
    # 변환기 실행
    converter = YouTubeHandleConverter(YOUTUBE_API_KEY)
    results = converter.convert_handles_to_ids(handles)
    
    # 결과 출력
    converter.print_results(results)
    
    # 채널 ID만 추출
    channel_ids = converter.get_channel_id_list(results)
    
    print("\n📋 채널 ID 리스트 (복사용):")
    print("-" * 60)
    print(channel_ids)
    print("\n또는 Python 코드:")
    print(f"channel_ids = {channel_ids}")
    
    # JSON 파일로 저장
    converter.save_to_json(results)
    
    print("\n💡 이제 이 채널 ID들을 첫 번째 스크래퍼 코드에 사용할 수 있습니다!")