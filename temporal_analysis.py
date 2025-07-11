#!/usr/bin/env python3
"""
時系列対応分析 - CSVの順序と動画の時間軸の相関を調査
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from src.lib.video_splitting.csv_parser import parse_qa_csv
from src.lib.video_splitting.whisper_analyzer import load_whisper_transcript
from src.lib.video_splitting.text_matcher import match_qa_with_whisper

def analyze_temporal_correlation():
    print("=== 時系列対応分析 ===")
    
    csv_path = "/home/ubuntu/attachments/42d2cd54-b84a-4545-97cb-a36fd26acd03/studio_results_20250710_2021.csv"
    whisper_json = "whisper_output/aianno_test.json"
    
    qa_segments = parse_qa_csv(csv_path)
    whisper_segments = load_whisper_transcript(whisper_json)
    
    print(f"Q&A総数: {len(qa_segments)}")
    print(f"Whisperセグメント数: {len(whisper_segments)}")
    
    print(f"\n=== CSV時系列分析 ===")
    if qa_segments:
        first_created = qa_segments[0]['created_at']
        last_created = qa_segments[-1]['created_at']
        print(f"最初のQ&A: {first_created}")
        print(f"最後のQ&A: {last_created}")
        
        created_times = [qa['created_at'] for qa in qa_segments]
        unique_times = list(set(created_times))
        unique_times.sort()
        
        print(f"ユニークなcreated_at数: {len(unique_times)}")
        print(f"時間範囲: {unique_times[0]} - {unique_times[-1]}")
    
    print(f"\n=== Whisper時系列分析 ===")
    if whisper_segments:
        whisper_start = min(seg['start'] for seg in whisper_segments)
        whisper_end = max(seg['end'] for seg in whisper_segments)
        print(f"音声範囲: {whisper_start:.1f}s - {whisper_end:.1f}s")
        print(f"動画長: {whisper_end:.1f}秒 ({whisper_end/60:.1f}分)")
    
    print(f"\n=== 現在のマッチング結果の時系列相関 ===")
    matches = match_qa_with_whisper(qa_segments, whisper_segments, 0.3)
    
    whisper_matches = [(i, match) for i, match in enumerate(matches) if match['whisper_segment'] is not None]
    
    if len(whisper_matches) >= 2:
        print(f"Whisperマッチ数: {len(whisper_matches)}")
        
        csv_indices = [i for i, match in whisper_matches]
        whisper_times = [match['whisper_segment']['start'] for i, match in whisper_matches]
        
        order_violations = 0
        for i in range(len(whisper_matches) - 1):
            csv_idx1, match1 = whisper_matches[i]
            csv_idx2, match2 = whisper_matches[i + 1]
            
            whisper_time1 = match1['whisper_segment']['start']
            whisper_time2 = match2['whisper_segment']['start']
            
            if csv_idx1 < csv_idx2 and whisper_time1 > whisper_time2:
                order_violations += 1
                print(f"順序違反: CSV#{csv_idx1}({whisper_time1:.1f}s) > CSV#{csv_idx2}({whisper_time2:.1f}s)")
        
        order_consistency = 1 - (order_violations / max(len(whisper_matches) - 1, 1))
        print(f"順序一致率: {order_consistency:.1%} ({order_violations}件の違反)")
        
        print(f"\n=== 詳細な時系列分析 ===")
        print("CSV順序 | Whisper時間 | 信頼度 | 質問")
        print("-" * 60)
        for i, (csv_idx, match) in enumerate(whisper_matches[:10]):
            whisper_time = match['whisper_segment']['start']
            confidence = match['confidence']
            query = match['qa']['query'][:30]
            print(f"{csv_idx:8d} | {whisper_time:10.1f}s | {confidence:6.3f} | {query}...")
    
    return whisper_matches

def propose_temporal_matching():
    print(f"\n=== 時系列考慮マッチング提案 ===")
    print("現在のアルゴリズムの問題点:")
    print("1. テキスト類似度のみでマッチング")
    print("2. CSV順序とWhisper時間軸の対応関係を無視")
    print("3. 時系列的に不整合なマッチを許可")
    
    print(f"\n改良案:")
    print("1. 時系列制約付きマッチング")
    print("   - CSV順序とWhisper時間の単調性を保証")
    print("   - 前のマッチより後の時間のみ候補とする")
    
    print("2. 時系列ボーナススコア")
    print("   - 順序が一致する場合に信頼度ボーナス")
    print("   - 時間間隔の妥当性を評価")
    
    print("3. グローバル最適化")
    print("   - 全体の時系列一致度を最大化")
    print("   - 動的プログラミングで最適解を探索")

if __name__ == '__main__':
    whisper_matches = analyze_temporal_correlation()
    propose_temporal_matching()
