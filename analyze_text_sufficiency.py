# -*- coding: utf-8 -*-
import pandas as pd
import json

def analyze_text_sufficiency():
    """각 클러스터의 텍스트 데이터 충분성 분석"""
    
    # 데이터 로드
    df = pd.read_csv('persona_clusters.csv')
    
    print("=" * 80)
    print("각 클러스터별 텍스트 데이터 충분성 분석")
    print("=" * 80)
    
    # 클러스터별 분석
    for cluster_id in sorted(df['cluster'].unique()):
        cluster_data = df[df['cluster'] == cluster_id]
        
        print(f"\n클러스터 {cluster_id}: {len(cluster_data)}개 채널")
        print("-" * 60)
        
        # STT 파일 수 통계
        total_stt_files = cluster_data['total_stt_files'].sum()
        avg_stt_files = cluster_data['total_stt_files'].mean()
        max_stt_files = cluster_data['total_stt_files'].max()
        min_stt_files = cluster_data['total_stt_files'].min()
        
        print(f"총 STT 파일 수: {total_stt_files}개")
        print(f"평균 STT 파일 수: {avg_stt_files:.1f}개")
        print(f"최대 STT 파일 수: {max_stt_files}개")
        print(f"최소 STT 파일 수: {min_stt_files}개")
        
        # 채널별 STT 파일 수
        print("\n채널별 STT 파일 수:")
        for _, row in cluster_data.iterrows():
            print(f"  - {row['channel_name']}: {row['total_stt_files']}개")
        
        # 충분성 평가
        print(f"\n충분성 평가:")
        if total_stt_files >= 50:
            print("  ✅ 충분함 (50개 이상)")
        elif total_stt_files >= 20:
            print("  ⚠️ 보통 (20-49개)")
        else:
            print("  ❌ 부족함 (20개 미만)")
        
        # 클러스터별 특징
        if cluster_id == 0:
            print("  📝 Emma 클러스터: emma chamberlain 단독, 20개 STT 파일")
        elif cluster_id == 1:
            print("  📝 Victoria 클러스터: 22개 채널, 다양한 STT 파일 수")
        elif cluster_id == 2:
            print("  📝 Misha 클러스터: 3개 채널, 높은 STT 파일 수")
        elif cluster_id == 3:
            print("  📝 Philip 클러스터: Philip Lemoine 단독, 50개 STT 파일")
        elif cluster_id == 4:
            print("  📝 James 클러스터: James Charles 단독, 10개 STT 파일")
    
    # 전체 요약
    print("\n" + "=" * 80)
    print("전체 요약")
    print("=" * 80)
    
    total_channels = len(df)
    total_stt_files = df['total_stt_files'].sum()
    avg_stt_per_channel = total_stt_files / total_channels
    
    print(f"총 채널 수: {total_channels}개")
    print(f"총 STT 파일 수: {total_stt_files}개")
    print(f"채널당 평균 STT 파일 수: {avg_stt_per_channel:.1f}개")
    
    # 클러스터별 STT 파일 수 요약
    print("\n클러스터별 STT 파일 수:")
    for cluster_id in sorted(df['cluster'].unique()):
        cluster_data = df[df['cluster'] == cluster_id]
        total_stt = cluster_data['total_stt_files'].sum()
        print(f"  클러스터 {cluster_id}: {total_stt}개")
    
    # 충분성 권장사항
    print("\n충분성 권장사항:")
    print("1. 클러스터 0 (Emma): 20개 - 보통 수준")
    print("2. 클러스터 1 (Victoria): 22개 채널 합계 - 충분함")
    print("3. 클러스터 2 (Misha): 3개 채널 합계 - 충분함")
    print("4. 클러스터 3 (Philip): 50개 - 충분함")
    print("5. 클러스터 4 (James): 10개 - 부족함")
    
    print("\n개선 방안:")
    print("- 클러스터 4 (James Charles)의 STT 파일 수가 부족함")
    print("- 더 많은 영상의 STT 데이터 수집 필요")
    print("- 각 클러스터별로 최소 20개 이상의 STT 파일 확보 권장")

if __name__ == "__main__":
    analyze_text_sufficiency()
