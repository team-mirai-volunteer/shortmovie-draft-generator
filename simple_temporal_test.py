#!/usr/bin/env python3
"""
時系列制約付きマッチングの簡単なテスト - 複雑なインポートを回避
"""

import sys
from pathlib import Path
import json
from difflib import SequenceMatcher
import re
from typing import List, Dict, Any

def normalize_for_matching(text: str) -> str:
    """マッチング用にテキストを正規化"""
    if not text:
        return ""
    text = re.sub(r'[^\w\s]', '', text.lower())
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def calculate_similarity_optimized(text1: str, text2: str) -> float:
    """最適化された類似度計算"""
    if not text1 or not text2:
        return 0.0
    
    base_similarity = SequenceMatcher(None, text1, text2).ratio()
    
    keywords = ['質問', '回答', 'について', 'ですか', 'でしょうか', 'ありがとう']
    bonus = 0.0
    for keyword in keywords:
        if keyword in text1 and keyword in text2:
            bonus += 0.05
    
    return min(1.0, base_similarity + bonus)

def calculate_temporal_bonus(current_time: float, last_time: float) -> float:
    """時系列ボーナススコアを計算"""
    if last_time < 0:
        return 0.1
    
    time_gap = current_time - last_time
    
    if 30 <= time_gap <= 120:
        return 0.3
    elif 10 <= time_gap < 30:
        return 0.2
    elif 120 < time_gap <= 300:
        return 0.1
    else:
        return 0.0

def simple_temporal_matching_test():
    """簡単な時系列マッチングテスト"""
    print("=== 簡単な時系列マッチングテスト ===")
    
    qa_samples = [
        {"id": "1", "query": "AIについて教えてください", "qtext": "AI", "text": "人工知能", "combined_text": "AI 人工知能"},
        {"id": "2", "query": "機械学習とは何ですか", "qtext": "機械学習", "text": "学習アルゴリズム", "combined_text": "機械学習 学習アルゴリズム"},
        {"id": "3", "query": "深層学習について", "qtext": "深層学習", "text": "ニューラルネットワーク", "combined_text": "深層学習 ニューラルネットワーク"},
    ]
    
    whisper_samples = [
        {"start": 10.0, "end": 25.0, "text": "人工知能について説明します", "duration": 15.0},
        {"start": 45.0, "end": 60.0, "text": "機械学習は重要な技術です", "duration": 15.0},
        {"start": 80.0, "end": 95.0, "text": "深層学習とニューラルネットワーク", "duration": 15.0},
    ]
    
    print(f"Q&Aサンプル: {len(qa_samples)}件")
    print(f"Whisperサンプル: {len(whisper_samples)}件")
    
    print("\n=== 従来のマッチング ===")
    old_matches = []
    used_indices = set()
    
    for qa in qa_samples:
        best_match = None
        best_score = 0
        
        for i, whisper in enumerate(whisper_samples):
            if i in used_indices:
                continue
            
            qa_text = normalize_for_matching(qa['combined_text'])
            whisper_text = normalize_for_matching(whisper['text'])
            
            score = calculate_similarity_optimized(qa_text, whisper_text)
            
            if score > best_score:
                best_score = score
                best_match = {"whisper": whisper, "score": score, "index": i}
        
        if best_match and best_match["score"] >= 0.3:
            old_matches.append({
                "qa": qa,
                "whisper": best_match["whisper"],
                "confidence": best_match["score"],
                "temporal_bonus": 0.0
            })
            used_indices.add(best_match["index"])
    
    print("\n=== 時系列制約付きマッチング ===")
    new_matches = []
    used_indices = set()
    last_matched_time = -1.0
    temporal_weight = 0.2
    
    for qa in qa_samples:
        best_match = None
        best_score = 0
        
        for i, whisper in enumerate(whisper_samples):
            if i in used_indices:
                continue
            
            if whisper["start"] <= last_matched_time:
                continue
            
            qa_text = normalize_for_matching(qa['combined_text'])
            whisper_text = normalize_for_matching(whisper['text'])
            
            text_score = calculate_similarity_optimized(qa_text, whisper_text)
            temporal_bonus = calculate_temporal_bonus(whisper["start"], last_matched_time)
            total_score = text_score + (temporal_weight * temporal_bonus)
            
            if total_score > best_score:
                best_score = total_score
                best_match = {
                    "whisper": whisper, 
                    "text_score": text_score,
                    "temporal_bonus": temporal_bonus,
                    "total_score": total_score, 
                    "index": i
                }
        
        if best_match and best_match["total_score"] >= 0.3:
            new_matches.append({
                "qa": qa,
                "whisper": best_match["whisper"],
                "confidence": best_match["total_score"],
                "text_similarity": best_match["text_score"],
                "temporal_bonus": best_match["temporal_bonus"]
            })
            used_indices.add(best_match["index"])
            last_matched_time = best_match["whisper"]["start"]
    
    print(f"\n=== 結果比較 ===")
    print(f"従来のマッチング: {len(old_matches)}件")
    print(f"時系列制約付き: {len(new_matches)}件")
    
    print(f"\n従来のマッチング詳細:")
    for i, match in enumerate(old_matches):
        qa = match["qa"]
        whisper = match["whisper"]
        print(f"  {i+1}. 質問: {qa['query']}")
        print(f"     Whisper: {whisper['text']}")
        print(f"     時間: {whisper['start']:.1f}s - {whisper['end']:.1f}s")
        print(f"     信頼度: {match['confidence']:.3f}")
    
    print(f"\n時系列制約付きマッチング詳細:")
    for i, match in enumerate(new_matches):
        qa = match["qa"]
        whisper = match["whisper"]
        print(f"  {i+1}. 質問: {qa['query']}")
        print(f"     Whisper: {whisper['text']}")
        print(f"     時間: {whisper['start']:.1f}s - {whisper['end']:.1f}s")
        print(f"     信頼度: {match['confidence']:.3f}")
        print(f"     - テキスト: {match['text_similarity']:.3f}")
        print(f"     - 時系列: {match['temporal_bonus']:.3f}")
    
    def check_order_violations(matches):
        violations = 0
        for i in range(len(matches) - 1):
            current_time = matches[i]['whisper']['start']
            next_time = matches[i + 1]['whisper']['start']
            if current_time > next_time:
                violations += 1
        return violations
    
    old_violations = check_order_violations(old_matches)
    new_violations = check_order_violations(new_matches)
    
    print(f"\n=== 順序一致性 ===")
    print(f"従来の順序違反: {old_violations}件")
    print(f"時系列制約付きの順序違反: {new_violations}件")
    
    if len(old_matches) > 1:
        old_consistency = 1 - (old_violations / max(len(old_matches) - 1, 1))
        print(f"従来の順序一致率: {old_consistency:.1%}")
    
    if len(new_matches) > 1:
        new_consistency = 1 - (new_violations / max(len(new_matches) - 1, 1))
        print(f"時系列制約付きの順序一致率: {new_consistency:.1%}")
    
    print(f"\n=== 結論 ===")
    print("時系列制約付きマッチングの効果:")
    print(f"- 順序違反の削減: {old_violations} → {new_violations}")
    print(f"- 時系列ボーナスによる適切な間隔の優遇")
    print(f"- CSV順序とWhisper時間軸の対応関係を考慮")

if __name__ == '__main__':
    simple_temporal_matching_test()
