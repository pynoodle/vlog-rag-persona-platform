# -*- coding: utf-8 -*-
import os
import sys
import json
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import yt_dlp
import whisper
import torch
from datetime import datetime
import glob
import time

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class YouTubeChannelScraper:
    def __init__(self, api_key, channel_id):
        """
        YouTube 채널 스크래퍼 초기화
        
        Args:
            api_key: YouTube Data API v3 키
            channel_id: YouTube 채널 ID (예: UCxxxxxx)
        """
        self.api_key = api_key
        self.channel_id = channel_id
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.whisper_model = None
        
        # GPU 사용 가능 여부 확인
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"STT에 사용할 디바이스: {self.device}")
        if self.device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        
    def get_latest_videos(self, max_results=10):
        """채널의 최신 영상 목록 가져오기"""
        print(f"채널의 최신 {max_results}개 영상을 가져오는 중...")
        
        # 채널의 업로드 플레이리스트 ID 가져오기
        channel_response = self.youtube.channels().list(
            part='contentDetails',
            id=self.channel_id
        ).execute()
        
        playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # 플레이리스트에서 영상 목록 가져오기
        videos = []
        request = self.youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=max_results
        )
        
        response = request.execute()
        
        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            videos.append(video_id)
            
        return videos
    
    def get_video_metadata(self, video_id):
        """영상의 메타데이터 가져오기"""
        print(f"영상 {video_id}의 메타데이터를 가져오는 중...")
        
        response = self.youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()
        
        if not response['items']:
            return None
            
        video = response['items'][0]
        
        metadata = {
            'video_id': video_id,
            'video_url': f'https://www.youtube.com/watch?v={video_id}',
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'published_at': video['snippet']['publishedAt'],
            'channel_title': video['snippet']['channelTitle'],
            'tags': video['snippet'].get('tags', []),
            'duration': video['contentDetails']['duration'],
            'view_count': video['statistics'].get('viewCount', 0),
            'like_count': video['statistics'].get('likeCount', 0),
            'comment_count': video['statistics'].get('commentCount', 0),
            'thumbnail_url': video['snippet']['thumbnails']['high']['url']
        }
        
        return metadata
    
    def get_transcript(self, video_id):
        """자막 가져오기 (한국어 우선)"""
        print(f"영상 {video_id}의 자막을 가져오는 중...")
        
        try:
            # 한국어 자막 시도
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            try:
                transcript = transcript_list.find_transcript(['ko'])
                fetched = transcript.fetch()
                time.sleep(0.5)  # 요청 사이 딜레이
                return [{'text': t['text'], 'start': t['start'], 'duration': t['duration']} for t in fetched], 'ko', 'subtitle'
            except:
                # 한국어 자막이 없으면 영어 시도
                try:
                    transcript = transcript_list.find_transcript(['en'])
                    fetched = transcript.fetch()
                    time.sleep(0.5)  # 요청 사이 딜레이
                    return [{'text': t['text'], 'start': t['start'], 'duration': t['duration']} for t in fetched], 'en', 'subtitle'
                except:
                    # 자동 생성 자막 시도
                    transcript = transcript_list.find_generated_transcript(['ko'])
                    fetched = transcript.fetch()
                    time.sleep(0.5)  # 요청 사이 딜레이
                    return [{'text': t['text'], 'start': t['start'], 'duration': t['duration']} for t in fetched], 'ko', 'auto-generated'
                    
        except (TranscriptsDisabled, NoTranscriptFound):
            print(f"영상 {video_id}에 자막이 없습니다. STT를 진행합니다...")
            return None, None, None
        except Exception as e:
            # IP 차단 등 다른 에러 처리
            if 'blocking' in str(e).lower() or 'banned' in str(e).lower():
                print(f"⚠️ YouTube 자막 API 차단 감지: {e}")
                print(f"   자막 없이 진행하거나 STT로 대체합니다...")
                return None, None, None
            else:
                print(f"자막 가져오기 에러: {e}")
                return None, None, None
    
    def download_audio(self, video_id, output_path='temp_audio'):
        """영상의 오디오만 다운로드"""
        print(f"영상 {video_id}의 오디오를 다운로드하는 중...")
        
        os.makedirs(output_path, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/{video_id}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            # 403 에러 및 IP 차단 방지를 위한 강화 옵션
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'web'],
                    'skip': ['hls', 'dash']
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.ios.youtube/19.09.3 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Sec-Fetch-Mode': 'navigate',
            },
            'retries': 5,
            'fragment_retries': 5,
            'sleep_interval': 1,  # 요청 사이 대기 시간
            'max_sleep_interval': 3,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            return f'{output_path}/{video_id}.mp3'
        except Exception as e:
            print(f"오디오 다운로드 실패: {e}")
            return None
    
    def transcribe_audio(self, audio_path, model_size='base'):
        """Whisper를 사용하여 오디오를 텍스트로 변환"""
        print(f"오디오를 텍스트로 변환하는 중... (모델: {model_size}, 디바이스: {self.device})")
        
        if self.whisper_model is None:
            print(f"Whisper 모델 로딩 중... ({self.device})")
            self.whisper_model = whisper.load_model(model_size, device=self.device)
        
        try:
            result = self.whisper_model.transcribe(audio_path, language='ko', fp16=(self.device == "cuda"))
            
            # YouTube 자막 형식과 유사하게 변환
            segments = []
            for segment in result['segments']:
                segments.append({
                    'text': segment['text'],
                    'start': segment['start'],
                    'duration': segment['end'] - segment['start']
                })
            
            return segments, 'ko', 'whisper-stt'
        except Exception as e:
            print(f"STT 변환 실패: {e}")
            return None, None, None
    
    def get_collected_video_ids(self, output_dir='youtube_data'):
        """이미 수집된 영상 ID 목록 가져오기"""
        channel_dir = os.path.join(output_dir, self.channel_id)
        if not os.path.exists(channel_dir):
            return set()
        
        collected_ids = set()
        # JSON 파일에서 video_id 추출
        json_files = glob.glob(f"{channel_dir}/*.json")
        for json_file in json_files:
            # channel_info.json은 제외
            if 'channel_info.json' in json_file:
                continue
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'metadata' in data and 'video_id' in data['metadata']:
                        collected_ids.add(data['metadata']['video_id'])
            except:
                # 파일명에서 video_id 추출 (파일명 형식: video_id_timestamp.json)
                filename = os.path.basename(json_file)
                video_id = filename.split('_')[0]
                collected_ids.add(video_id)
        
        return collected_ids
    
    def save_data(self, video_data, output_dir='youtube_data'):
        """데이터를 파일로 저장"""
        # 채널별 폴더 생성 (채널 ID로 구분)
        channel_dir = os.path.join(output_dir, self.channel_id)
        os.makedirs(channel_dir, exist_ok=True)
        
        video_id = video_data['metadata']['video_id']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 메타데이터와 전사본을 하나의 JSON 파일로 저장
        output_file = f"{channel_dir}/{video_id}_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, ensure_ascii=False, indent=2)
        
        print(f"데이터 저장 완료: {output_file}")
        
        # 자막/전사본을 별도의 텍스트 파일로도 저장
        if video_data.get('transcript'):
            txt_file = f"{channel_dir}/{video_id}_{timestamp}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"제목: {video_data['metadata']['title']}\n")
                f.write(f"URL: {video_data['metadata']['video_url']}\n")
                f.write(f"전사 타입: {video_data['transcript_type']}\n\n")
                
                for segment in video_data['transcript']:
                    start_time = segment['start']
                    text = segment['text']
                    f.write(f"[{start_time:.2f}s] {text}\n")
            
            print(f"텍스트 파일 저장 완료: {txt_file}")
    
    def process_videos(self, max_videos=10, use_stt=True, whisper_model='base', skip_transcript_api=False):
        """전체 프로세스 실행
        
        Args:
            max_videos: 수집할 최대 영상 수
            use_stt: 자막이 없을 때 STT 사용 여부
            whisper_model: Whisper 모델 크기
            skip_transcript_api: True면 자막 API를 건너뛰고 바로 STT 사용 (IP 차단 시)
        """
        print(f"\n{'='*50}")
        print(f"YouTube 채널 영상 수집 시작")
        if skip_transcript_api:
            print(f"⚠️ 자막 API 건너뛰기 모드 (IP 차단 우회)")
        print(f"{'='*50}\n")
        
        # 이미 수집된 영상 ID 목록 가져오기
        collected_ids = self.get_collected_video_ids()
        if collected_ids:
            print(f"이미 수집된 영상: {len(collected_ids)}개")
        
        # 최신 영상 목록 가져오기
        video_ids = self.get_latest_videos(max_videos)
        
        # 새로운 영상만 필터링
        new_video_ids = [vid for vid in video_ids if vid not in collected_ids]
        skipped_count = len(video_ids) - len(new_video_ids)
        
        if skipped_count > 0:
            print(f"중복 건너뛰기: {skipped_count}개")
        if new_video_ids:
            print(f"새로운 영상: {len(new_video_ids)}개\n")
        else:
            print("수집할 새로운 영상이 없습니다.\n")
            return []
        
        # 채널 정보 파일 저장
        channel_info_dir = f"youtube_data/{self.channel_id}"
        os.makedirs(channel_info_dir, exist_ok=True)
        channel_info_file = f"{channel_info_dir}/channel_info.json"
        
        # 첫 번째 영상의 메타데이터에서 채널 정보 가져오기
        first_metadata = self.get_video_metadata(new_video_ids[0])
        if first_metadata:
            # 기존 channel_info가 있으면 읽어오기
            total_collected = len(collected_ids) + len(new_video_ids)
            channel_info = {
                'channel_id': self.channel_id,
                'channel_title': first_metadata['channel_title'],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_videos_collected': total_collected
            }
            with open(channel_info_file, 'w', encoding='utf-8') as f:
                json.dump(channel_info, f, ensure_ascii=False, indent=2)
            print(f"채널 정보 업데이트: {channel_info_file}\n")
        
        results = []
        
        for idx, video_id in enumerate(new_video_ids, 1):
            print(f"\n[{idx}/{len(new_video_ids)}] 처리 중: {video_id}")
            print("-" * 50)
            
            # 메타데이터 수집
            metadata = self.get_video_metadata(video_id)
            if not metadata:
                print(f"메타데이터를 가져올 수 없습니다. 건너뜁니다.")
                continue
            
            video_data = {
                'metadata': metadata,
                'transcript': None,
                'transcript_language': None,
                'transcript_type': None
            }
            
            # 자막 가져오기 시도
            transcript = None
            lang = None
            trans_type = None
            
            if not skip_transcript_api:
                transcript, lang, trans_type = self.get_transcript(video_id)
            else:
                print(f"자막 API 건너뛰기 - STT로 직접 진행")
            
            if transcript:
                video_data['transcript'] = transcript
                video_data['transcript_language'] = lang
                video_data['transcript_type'] = trans_type
                print(f"자막 수집 완료 (언어: {lang}, 타입: {trans_type})")
            elif use_stt:
                # 자막이 없으면 STT 수행
                audio_path = self.download_audio(video_id)
                
                if audio_path and os.path.exists(audio_path):
                    transcript, lang, trans_type = self.transcribe_audio(audio_path, whisper_model)
                    
                    if transcript:
                        video_data['transcript'] = transcript
                        video_data['transcript_language'] = lang
                        video_data['transcript_type'] = trans_type
                        print(f"STT 변환 완료 (언어: {lang})")
                    
                    # 임시 오디오 파일 삭제
                    try:
                        os.remove(audio_path)
                    except:
                        pass
            
            # 데이터 저장
            self.save_data(video_data)
            results.append(video_data)
            
            # 영상 처리 사이 딜레이 (IP 차단 방지)
            time.sleep(1)
        
        print(f"\n{'='*50}")
        print(f"처리 완료! 새로 수집: {len(results)}개, 전체: {len(collected_ids) + len(results)}개")
        print(f"{'='*50}\n")
        
        return results


if __name__ == "__main__":
    # ======== 설정 ========
    
    # ⚠️ IP 차단 경고가 나타나면 아래 옵션들을 변경하세요
    
    # 옵션 1: 자막 API 건너뛰기 (자막 없이 STT만 사용)
    SKIP_TRANSCRIPT_API = True  # IP 차단으로 인해 True로 변경
    
    # 옵션 2: STT 사용 (중요!)
    # False면 메타데이터만 수집, True면 Whisper로 음성을 텍스트로 변환
    USE_STT = True  # True: STT 사용 (권장), False: 메타데이터만 수집
    
    # 여러 API 키를 순환 사용하여 쿼터 제한 우회
    # 환경 변수에서 YouTube API 키를 콤마로 구분해 여러 개 설정 가능
    # 예: YOUTUBE_API_KEYS=key1,key2,key3
    import os
    _keys_str = os.getenv("YOUTUBE_API_KEYS", os.getenv("YOUTUBE_API_KEY", ""))
    API_KEYS = [k.strip() for k in _keys_str.split(",") if k.strip()]
    
    # 수집할 채널 ID 리스트 (채널 URL에서 확인)
    CHANNEL_IDS = [
       # "UCJvR4zNAPRJoMDF3A912dBA", 
       #  
       # top30 popular genz influencers
        #'UCWkYXtnAuu7VTLPwUcRSB6A', 'UCi3OE-aN09WOcN9d2stCvPg', 'UCAgIfWgzZ6QtvB_Oj1SBNnA', 'UC86suRFnqiw8zN6LIYxddYQ', 'UC78cxCAcp7JfQPgKxYdyGrg', 'UCJ48BrODPTg4RJBLNIj9J1Q', 'UCTn6eUt2dRO_iaH_q49yHzg', 'UCIfeSCjbA3koG9u7RHrrrOg', 'UC3EFKdXAU99j3ppGgvTz7XQ', 'UC-F3kTU4V680v550AavEOsQ', 'UC6QWhGQqf0YDYdRb0n6ojWw', 'UCucot-Zp428OwkyRm2I7v2Q', 'UCy96nw0qjQYc6WJZ8odwioQ', 'UCvTX9IDOCS_Ax2v0zN8PuwA', 'UC_CICrZWlIAyraLU7T1NBGw', 'UCf5Z8I0Yy0_-a-xAu2_0Yiw', 'UCiGWpX9oCmMu3hRUV_ZBvpg'# Emma Chamberlain
        # iphone vlogger list
        'UCaUgbmxXHCTXXkaJdmbuyIA', 'UCdc8lZHOvCQC89AUvN5nYdg', 
        'UC_0RAMKsGbvNujWt6RZZHIw', 'UCA6fMo3G4PNCuw6Ndzdo_Xg', 
        'UCb4aFIfcJZY8y2T2MkKD2eg', 'UCIPigoUn9DZl6XSuBxoydQg', 
        'UCvs8YG-yhlHx9qiq8Akrgrw', 'UC6go9qixF_GnKTbn2AGiYKQ', 
        'UCvAHILjsHJF9r2qSS-BAmYA', 'UCCeXwLzVKZU7VW8qXis_UOQ', 
        'UCW-ORpg24g63xBDew6xEyTA', 'UCmWRQG-1pbzNyjl6FQ6oNtQ', 
        'UCvrgf-Y45oJBw1AQYTDNDmA', 'UCB90rkvVhNL-pFqG0xGJtmA', 
        'UCKbeOEcrZb48MKR50EPgKHg', 'UCnz2_V9spAVIQXlTBFsWq1Q', 
        'UC5-E_dowa1WfHYz6eSTGTHQ', 'UCe1rRMQKy5JK7jFRZ_6pBtA', 
        'UCdUs3rJr3d1s-3Txm020-4A', 'UClaYO_c9NCWYWiontYW9i-Q', 
        'UCcD-DpQztF3fymfagC73fYg', 'UCLW0s6QUE-k87R9XQ7G3hTQ', 
        'UCDOJLR72Jj-lEviJdwU4G6g', 'UCg9BcSjR7l30TfgOvichwxw', 
        'UCfldmO5aM5zFpoA7pnPWB8A', 'UCbgqlUD84KKSujlUkmJNeDg', 
        'UCaW4E4J01Q5dmAAj8gezC_w', 'UCcyoi1KF9tpmlNWTFuBVk6A', 
        'UCxwZdNG1O66quSv9YK6CHmw', 'UCsJmcwKLnwPkwCCD8nXB5LQ', 
        'UCxNhswggApcm_ZpfWM-ihsg', 'UCxw_JBZaRWtL6JKvyxdUx5g', 
        'UCJXwJLW_RY-5zgOiyar3hYQ', 'UCoZ1s8gr_CycBLdWND-1HPA', 
        'UCqFilu6VGpDx-4B_g2jX0Xg', 'UCXwpFRuIEVQ6aSxN_uM1ldA', 
        'UCjFFNcfgIpKFuoqrBc7-iXQ', 'UC2cFvIqq9J10Vwx6kw3Mfvg', 
        'UC5W81PwG9xqUReQH2TW404Q', 'UC6BBzTpa1YF96JuPUMT9mWQ', 
        'UCvXd-ZMUYbQrj5EZCbkL7Mw', 'UC5uKMjPmITdRSA0405FFjug', 
        'UClf7V2Uqsp8bPrlXry0iTTA', 'UCP2uTYjohuUQklN1f9MFwrg', 
        'UCvd9M7scKQHzerck6tcYL-g', 'UC9GrfBvC7EDV9NsUDByDq3w', 
        'UCDMiCblpBbr6WqvodoV85xQ', 'UCSAazAJIiHDXYX7f4PRhjcg', 
        'UCaUpqLv4erEjme4YNquy2Qg', 'UC9PfekKMDzLt_tkragAeACw', 
        'UCRKAb1fHSOtLWDBi35ZDUvw', 'UCzrzxvTa2dHeNav7zl9L4Ug', 
        'UCfQx-K9zBExhMLfKQmXBxJg', 'UC5_cjRMuwhmEjj1Mh39JruQ', 
        
        'UCdrH8TMXN5dkomY0TKe7RIA', 'UC1J7puPhNHMONfKfCsNdTjQ', 
        'UCRtRPH0dz7THZLO9-NHFQbg', 'UCSucMa4aaOYOXe3y7IhelmA', 
        'UCP0R1BiTra_nLQXXyn4PzVQ', 'UCm0cV6cEa6iAgWSqBCyEndg', 
        'UCFM3hijh6mzg9buViYfbemQ', 'UCTt4TrACVRizUg73yO8fvdw', 
        'UCFmwE7aP8T_8FbuJS8lbdUQ', 'UCa3ylSmA2dg2tDmAeDsfaSg', 
        'UCff8p7TZgXxq3A6byvMH2CA', 'UCqRjPZ0vCzlAXCanFI3Fxrg', 
        'UCvxd9_WzHuPQcXPz8ODyfWA', 'UCyIRhcmxbD0nnAXX6Z8gvag', 'UCh7sFvTDwhy0ysjEqbVdABQ', 
        'UCyiyMB7zw_uIpID2rXC-0wA', 'UCiZoaJo2nM2D-gEUHpkJfhw', 'UCKYmTpdCkWK-gIdkxGK9S_A', 
        'UCA0oZ63wytik-f8HCz_umEQ', 'UCyAriCU7bpinmBzH_u5w4kw', 'UCjpU9XkqxBFvASqLTGrG8BA', 
        'UCWlNWKU7cn3fTxWJt1bw3mg', 'UCVKOBq9zfHIT9j7ZqPASKBQ', 'UCDUyDv6rywPxhdeRyA_KY4A', 
        'UCKWDKVjk2qcvRUShkUofkiw', 'UCKaCalz5N5ienIbfPzEbYuA', 'UCrs_Di9lLls_nvWnPNvk6OQ', 
        'UCqJ0QnHfvPMTSzxoWa-X9FQ', 'UCGbdpXT0waDfg330LsyzDEg', 'UCUfYnCDgbm6fKoJ9Gf7THfA', 'UCZI1v9kPAcr2rjp51SkDWhg',
         'UC3SafDS4jxWKROqzPaON0lA', 'UCrJv75V4Mh3tBmFwS_6b3mw', 'UCvPfa7yll5K_7VG5hA9lZVQ', 'UC8jtW4wcC226-zwBsLYUcDQ',
          'UCd0iAIdZxOGEgBBco9jaP4A', 'UC7xMBGa8dy0xVbhjNIY-nPg', 'UC7U_OqXVkRdGHxiUo4t9LgQ', 
          'UCuGHfFf4exFrBRAqy9cJAdg', 'UCq2GutDFXrztWzwiYmNv2HA', 'UCFW-K3Oor0MgElsg-6SfieA', 
          'UCeJICuSKNGMVQbAAzH6DcAw', 'UCzVfNcVh8Oj1rJgq1tjgF_w', 'UC46jnLaai5IRmHmuuHzx8sg', 
          'UCXm30w3cPvoZT3wZNRj9Jng', 'UCzbEcp0Lg1RiNJcnobwm5Sw'
    ]
    
    # 전체 결과 저장
    all_results = {}
    api_key_usage = {i: 0 for i in range(len(API_KEYS))}  # API 키별 사용 횟수 추적
    
    # 초기 API 키 설정
    print(f"\n{'='*70}")
    print(f"🔑 사용 가능한 API 키: {len(API_KEYS)}개")
    print(f"   각 채널마다 자동으로 순환 사용하여 쿼터 분산!")
    print(f"{'='*70}\n")
    
    # 각 채널별로 스크래퍼 실행
    for idx, channel_id in enumerate(CHANNEL_IDS, 1):
        print(f"\n{'='*70}")
        print(f"채널 [{idx}/{len(CHANNEL_IDS)}] 처리 중: {channel_id}")
        print(f"{'='*70}")
        
        # API 키 순환 사용
        api_key_tried = 0
        success = False
        
        while api_key_tried < len(API_KEYS) and not success:
            # 현재 API 키 선택
            current_key_idx = (idx - 1 + api_key_tried) % len(API_KEYS)
            current_api_key = API_KEYS[current_key_idx]
            
            print(f"🔑 API 키 [{current_key_idx + 1}/{len(API_KEYS)}] 사용 중...")
            
            try:
                # 스크래퍼 초기화
                scraper = YouTubeChannelScraper(current_api_key, channel_id)
            
                # 최신 100개 영상 처리
                # use_stt=True: 자막이 없으면 STT 수행
                # whisper_model: 'tiny', 'base', 'small', 'medium', 'large' 중 선택
                #                (크기가 클수록 정확도 높지만 속도 느림)
                # skip_transcript_api=True: IP 차단 시 자막 API를 건너뛰고 STT만 사용
                results = scraper.process_videos(
                    max_videos=100,
                    use_stt=USE_STT,
                    whisper_model='base',
                    skip_transcript_api=SKIP_TRANSCRIPT_API
                )
                
                all_results[channel_id] = results
                success = True
                api_key_usage[current_key_idx] += 1  # API 키 사용 횟수 증가
                
                print(f"\n✓ 채널 {channel_id}: {len(results)}개 영상 수집 완료 (API 키 #{current_key_idx + 1})")
                
            except Exception as e:
                error_msg = str(e)
                
                # API 쿼터 에러 체크
                if 'quota' in error_msg.lower() or 'limit' in error_msg.lower() or '403' in error_msg:
                    print(f"\n⚠️ API 쿼터 제한! 다음 API 키로 전환합니다...")
                    api_key_tried += 1
                    
                    if api_key_tried >= len(API_KEYS):
                        print(f"\n❌ 모든 API 키의 쿼터가 소진되었습니다!")
                        print(f"   내일 다시 시도하거나 새로운 API 키를 추가하세요.")
                        break
                else:
                    # 다른 에러는 바로 종료
                    print(f"\n✗ 채널 {channel_id} 처리 중 에러 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    break
        
        if not success:
            print(f"\n⚠️ 채널 {channel_id} 수집 실패 - 다음 채널로 이동...")
            continue
    
    # 전체 수집 결과 요약
    print(f"\n{'='*70}")
    print(f"전체 수집 완료!")
    print(f"{'='*70}")
    print(f"총 {len(CHANNEL_IDS)}개 채널, {sum(len(v) for v in all_results.values())}개 영상 수집\n")
    
    # API 키 사용 통계
    print(f"{'─'*70}")
    print(f"🔑 API 키 사용 통계:")
    print(f"{'─'*70}")
    for key_idx, usage_count in api_key_usage.items():
        if usage_count > 0:
            print(f"   API 키 #{key_idx + 1}: {usage_count}개 채널 처리")
    print()
    
    for channel_id, results in all_results.items():
        if results:
            print(f"\n채널: {channel_id} ({results[0]['metadata']['channel_title']})")
            print(f"수집된 영상: {len(results)}개")
            for video in results:
                print(f"  - {video['metadata']['title']}")
                print(f"    조회수: {video['metadata']['view_count']}, 좋아요: {video['metadata']['like_count']}")
                print(f"    자막/STT: {video['transcript_type']}")
            print()
