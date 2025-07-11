#!/usr/bin/env python3
"""
時系列制約付きマッチングと従来のマッチングの比較分析
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.lib.video_splitting.csv_parser import parse_qa_csv
from src.lib.video_splitting.whisper_analyzer import load_whisper_transcript
from src.lib.video_splitting.text_matcher import match_qa_with_whisper, match_qa_with_whisper_temporal

def analyze_temporal_improvement():
    """時系列制約付きマッチングの改善効果を分析"""
    print("=== 時系列制約付きマッチング比較分析 ===")
    
    csv_path = "/home/ubuntu/attachments/42d2cd54-b84a-4545-97cb-a36fd26acd03/studio_results_20250710_2021.csv"
    whisper_json = "whisper_output/aianno_test.json"
    
    qa_segments = parse_qa_csv(csv_path)
    whisper_segments = load_whisper_transcript(whisper_json)
    
    print(f"Q&A総数: {len(qa_segments)}")
    print(f"Whisperセグメント数: {len(whisper_segments)}")
    
    print("\n=== 従来のマッチング ===")
    old_matches = match_qa_with_whisper(qa_segments, whisper_segments, 0.3)
    
    temporal_weights = [0.1, 0.2, 0.3]
    results = {}
    
    for weight in temporal_weights:
        print(f"\n=== 時系列制約付きマッチング (weight={weight}) ===")
        new_matches = match_qa_with_whisper_temporal(qa_segments, whisper_segments, 0.3, weight)
        results[weight] = new_matches
    
    old_whisper_matches = [m for m in old_matches if m['whisper_segment'] is not None]
    
    print(f"\n=== 比較結果 ===")
    print(f"従来のマッチング: {len(old_whisper_matches)}件")
    
    if old_whisper_matches:
        old_avg_conf = sum(m['confidence'] for m in old_whisper_matches) / len(old_whisper_matches)
        old_violations = calculate_order_violations(old_whisper_matches)
        old_consistency = 1 - (old_violations / max(len(old_whisper_matches) - 1, 1))
        print(f"従来の平均信頼度: {old_avg_conf:.3f}")
        print(f"従来の順序一致率: {old_consistency:.1%} ({old_violations}件の違反)")
    
    for weight, new_matches in results.items():
        new_whisper_matches = [m for m in new_matches if m['whisper_segment'] is not None]
        print(f"\n時系列制約付き (weight={weight}): {len(new_whisper_matches)}件")
        
        if new_whisper_matches:
            new_avg_conf = sum(m['confidence'] for m in new_whisper_matches) / len(new_whisper_matches)
            new_avg_text = sum(m.get('text_similarity', 0) for m in new_whisper_matches) / len(new_whisper_matches)
            new_avg_temporal = sum(m.get('temporal_bonus', 0) for m in new_whisper_matches) / len(new_whisper_matches)
            new_violations = calculate_order_violations(new_whisper_matches)
            new_consistency = 1 - (new_violations / max(len(new_whisper_matches) - 1, 1))
            
            print(f"  平均信頼度: {new_avg_conf:.3f}")
            print(f"  - テキスト類似度: {new_avg_text:.3f}")
            print(f"  - 時系列ボーナス: {new_avg_temporal:.3f}")
            print(f"  順序一致率: {new_consistency:.1%} ({new_violations}件の違反)")
    
    return old_matches, results

def calculate_order_violations(whisper_matches):
    """順序違反の数を計算"""
    violations = 0
    for i in range(len(whisper_matches) - 1):
        current_time = whisper_matches[i]['whisper_segment']['start']
        next_time = whisper_matches[i + 1]['whisper_segment']['start']
        
        if current_time > next_time:
            violations += 1
    
    return violations

if __name__ == '__main__':
    analyze_temporal_improvement()
