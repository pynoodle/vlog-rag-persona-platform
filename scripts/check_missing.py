# -*- coding: utf-8 -*-
import os
import sys
import json

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# youtube_scraper.py의 채널 ID 리스트 확인
channel_ids_in_script = [
    'UCaUgbmxXHCTXXkaJdmbuyIA', 'UCdc8lZHOvCQC89AUvN5nYdg', 'UC_0RAMKsGbvNujWt6RZZHIw', 'UCA6fMo3G4PNCuw6Ndzdo_Xg', 'UCb4aFIfcJZY8y2T2MkKD2eg', 'UCIPigoUn9DZl6XSuBxoydQg', 'UCvs8YG-yhlHx9qiq8Akrgrw', 'UC6go9qixF_GnKTbn2AGiYKQ', 'UCvAHILjsHJF9r2qSS-BAmYA', 'UCCeXwLzVKZU7VW8qXis_UOQ', 'UCW-ORpg24g63xBDew6xEyTA', 'UCmWRQG-1pbzNyjl6FQ6oNtQ', 'UCvrgf-Y45oJBw1AQYTDNDmA', 'UCB90rkvVhNL-pFqG0xGJtmA', 'UCKbeOEcrZb48MKR50EPgKHg', 'UCnz2_V9spAVIQXlTBFsWq1Q', 'UC5-E_dowa1WfHYz6eSTGTHQ', 'UCe1rRMQKy5JK7jFRZ_6pBtA', 'UCdUs3rJr3d1s-3Txm020-4A', 'UClaYO_c9NCWYWiontYW9i-Q', 'UCcD-DpQztF3fymfagC73fYg', 'UCLW0s6QUE-k87R9XQ7G3hTQ', 'UCDOJLR72Jj-lEviJdwU4G6g', 'UCg9BcSjR7l30TfgOvichwxw', 'UCfldmO5aM5zFpoA7pnPWB8A', 'UCbgqlUD84KKSujlUkmJNeDg', 'UCaW4E4J01Q5dmAAj8gezC_w', 'UCcyoi1KF9tpmlNWTFuBVk6A', 'UCxwZdNG1O66quSv9YK6CHmw', 'UCsJmcwKLnwPkwCCD8nXB5LQ', 'UCxNhswggApcm_ZpfWM-ihsg', 'UCxw_JBZaRWtL6JKvyxdUx5g', 'UCJXwJLW_RY-5zgOiyar3hYQ', 'UCoZ1s8gr_CycBLdWND-1HPA', 'UCqFilu6VGpDx-4B_g2jX0Xg', 'UCXwpFRuIEVQ6aSxN_uM1ldA', 'UCjFFNcfgIpKFuoqrBc7-iXQ', 'UC2cFvIqq9J10Vwx6kw3Mfvg', 'UC5W81PwG9xqUReQH2TW404Q', 'UC6BBzTpa1YF96JuPUMT9mWQ', 'UCvXd-ZMUYbQrj5EZCbkL7Mw', 'UC5uKMjPmITdRSA0405FFjug', 'UClf7V2Uqsp8bPrlXry0iTTA', 'UCP2uTYjohuUQklN1f9MFwrg', 'UCvd9M7scKQHzerck6tcYL-g', 'UC9GrfBvC7EDV9NsUDByDq3w', 'UCDMiCblpBbr6WqvodoV85xQ', 'UCSAazAJIiHDXYX7f4PRhjcg', 'UCaUpqLv4erEjme4YNquy2Qg', 'UC9PfekKMDzLt_tkragAeACw', 'UCRKAb1fHSOtLWDBi35ZDUvw', 'UCzrzxvTa2dHeNav7zl9L4Ug', 'UCfQx-K9zBExhMLfKQmXBxJg', 'UC5_cjRMuwhmEjj1Mh39JruQ', 'UCdrH8TMXN5dkomY0TKe7RIA', 'UC1J7puPhNHMONfKfCsNdTjQ', 'UCRtRPH0dz7THZLO9-NHFQbg', 'UCSucMa4aaOYOXe3y7IhelmA', 'UCP0R1BiTra_nLQXXyn4PzVQ', 'UCm0cV6cEa6iAgWSqBCyEndg', 'UCFM3hijh6mzg9buViYfbemQ', 'UCTt4TrACVRizUg73yO8fvdw', 'UCFmwE7aP8T_8FbuJS8lbdUQ', 'UCa3ylSmA2dg2tDmAeDsfaSg', 'UCff8p7TZgXxq3A6byvMH2CA', 'UCqRjPZ0vCzlAXCanFI3Fxrg', 'UCvxd9_WzHuPQcXPz8ODyfWA', 'UCyIRhcmxbD0nnAXX6Z8gvag', 'UCh7sFvTDwhy0ysjEqbVdABQ', 'UCyiyMB7zw_uIpID2rXC-0wA', 'UCiZoaJo2nM2D-gEUHpkJfhw', 'UCKYmTpdCkWK-gIdkxGK9S_A', 'UCA0oZ63wytik-f8HCz_umEQ', 'UCyAriCU7bpinmBzH_u5w4kw', 'UCjpU9XkqxBFvASqLTGrG8BA', 'UCWlNWKU7cn3fTxWJt1bw3mg', 'UCVKOBq9zfHIT9j7ZqPASKBQ', 'UCDUyDv6rywPxhdeRyA_KY4A', 'UCKWDKVjk2qcvRUShkUofkiw', 'UCKaCalz5N5ienIbfPzEbYuA', 'UCrs_Di9lLls_nvWnPNvk6OQ', 'UCqJ0QnHfvPMTSzxoWa-X9FQ', 'UCGbdpXT0waDfg330LsyzDEg', 'UCUfYnCDgbm6fKoJ9Gf7THfA', 'UCZI1v9kPAcr2rjp51SkDWhg', 'UC3SafDS4jxWKROqzPaON0lA', 'UCrJv75V4Mh3tBmFwS_6b3mw', 'UCvPfa7yll5K_7VG5hA9lZVQ', 'UC8jtW4wcC226-zwBsLYUcDQ', 'UCd0iAIdZxOGEgBBco9jaP4A', 'UC7xMBGa8dy0xVbhjNIY-nPg', 'UC7U_OqXVkRdGHxiUo4t9LgQ', 'UCuGHfFf4exFrBRAqy9cJAdg', 'UCq2GutDFXrztWzwiYmNv2HA', 'UCFW-K3Oor0MgElsg-6SfieA', 'UCeJICuSKNGMVQbAAzH6DcAw', 'UCzVfNcVh8Oj1rJgq1tjgF_w', 'UC46jnLaai5IRmHmuuHzx8sg', 'UCXm30w3cPvoZT3wZNRj9Jng', 'UCzbEcp0Lg1RiNJcnobwm5Sw'
]

data_dir = 'youtube_data'

if not os.path.exists(data_dir):
    print("youtube_data 폴더가 없습니다.")
    exit()

# 실제 수집된 채널 확인
collected_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]

# 영상이 있는 채널과 없는 채널 구분
channels_with_videos = []
channels_without_videos = []

for channel_id in collected_dirs:
    channel_path = os.path.join(data_dir, channel_id)
    
    # 채널 이름 가져오기
    channel_info_path = os.path.join(channel_path, 'channel_info.json')
    channel_name = channel_id
    if os.path.exists(channel_info_path):
        try:
            with open(channel_info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
                channel_name = info.get('channel_title', channel_id)
        except:
            pass
    
    # 영상 파일 수 확인
    json_files = [f for f in os.listdir(channel_path) if f.endswith('.json') and 'channel_info' not in f]
    video_count = len(json_files)
    
    if video_count > 0:
        channels_with_videos.append((channel_id, channel_name, video_count))
    else:
        channels_without_videos.append((channel_id, channel_name))

# 아예 시도되지 않은 채널
not_attempted = [cid for cid in channel_ids_in_script if cid not in collected_dirs]

print("\n" + "="*70)
print("📊 채널 수집 상태 분석")
print("="*70 + "\n")

print(f"📋 스크립트에 등록된 채널: {len(channel_ids_in_script)}개")
print(f"✅ 영상 수집 완료: {len(channels_with_videos)}개")
print(f"⚠️  폴더는 있지만 영상 없음: {len(channels_without_videos)}개")
print(f"❌ 시도조차 안 됨: {len(not_attempted)}개\n")

if channels_without_videos:
    print("="*70)
    print("⚠️  영상이 수집되지 않은 채널 (폴더만 생성됨):")
    print("="*70)
    for idx, (channel_id, channel_name) in enumerate(channels_without_videos, 1):
        print(f"{idx:2d}. {channel_name} ({channel_id})")
    print()

if not_attempted:
    print("="*70)
    print("❌ 아직 시도되지 않은 채널:")
    print("="*70)
    print(f"총 {len(not_attempted)}개 채널이 아직 처리되지 않았습니다.")
    print("→ 스크립트가 중간에 중단되었거나, 이 채널들은 아직 처리 순서가 오지 않았습니다.\n")
    
print("💡 해결 방법:")
print("   1. youtube_scraper.py를 다시 실행하면 나머지 채널들을 계속 수집합니다")
print("   2. 기존에 수집된 영상은 자동으로 건너뛰므로 중복 걱정 없습니다")
print("   3. 에러가 발생한 채널은 로그를 확인하여 문제를 파악하세요\n")

