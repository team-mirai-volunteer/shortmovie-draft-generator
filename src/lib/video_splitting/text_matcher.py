from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher
import re


def match_qa_with_whisper(qa_segments: List[Dict], whisper_segments: List[Dict], confidence_threshold: float = 0.3) -> List[Dict]:
    """Q&AセグメントとWhisperセグメントをマッチング（完全重複回避版）"""
    matches = []
    used_whisper_indices = set()
    allocated_timings = []  # 既に割り当てられた時間範囲を追跡
    total_qa = len(qa_segments)
    
    print("Whisperセグメントのテキストを正規化中...")
    normalized_whisper_texts = []
    for segment in whisper_segments:
        normalized_whisper_texts.append(normalize_for_matching(segment['text']))
    
    print(f"Q&Aマッチング開始: {total_qa}件を処理中...")

    for i, qa in enumerate(qa_segments):
        if i % 100 == 0:  # 100件ごとに進捗表示
            print(f"進捗: {i}/{total_qa} ({i/total_qa*100:.1f}%)")
        
        best_match = find_best_whisper_match_optimized(qa, whisper_segments, normalized_whisper_texts, used_whisper_indices)

        if best_match and best_match["confidence"] >= confidence_threshold:
            segment = best_match["segment"]
            buffered_start = max(0, segment["start"] - 2)
            buffered_end = min(1500, segment["end"] + 2)
            allocated_timings.append((buffered_start, buffered_end))
            
            matches.append({"qa": qa, "whisper_segment": best_match["segment"], "confidence": best_match["confidence"], "match_type": best_match["match_type"]})
            used_whisper_indices.add(best_match["index"])
        else:
            estimated_timing = find_non_overlapping_slot(allocated_timings, 15, 1500)
            allocated_timings.append((estimated_timing["start"], estimated_timing["end"]))
            
            matches.append({"qa": qa, "whisper_segment": None, "estimated_timing": estimated_timing, "confidence": 0.0, "match_type": "estimated"})

    print(f"マッチング完了: {total_qa}件処理済み")
    return matches


def find_best_whisper_match_optimized(qa: Dict, whisper_segments: List[Dict], 
                                     normalized_whisper_texts: List[str], used_indices: set) -> Dict:
    """単一のQ&Aに対する最適なWhisperセグメントを検索（最適化版）"""
    best_match = None
    best_score = 0
    
    qa_texts = {
        'qtext': normalize_for_matching(qa['qtext']),
        'text': normalize_for_matching(qa['text']),
        'combined': normalize_for_matching(qa['combined_text']),
        'query': normalize_for_matching(qa['query'])
    }

    for i, segment in enumerate(whisper_segments):
        if i in used_indices:
            continue
        
        normalized_whisper_text = normalized_whisper_texts[i]
        
        if not normalized_whisper_text:
            continue
        
        scores = {}
        for key, qa_text in qa_texts.items():
            if qa_text:  # 空でない場合のみ計算
                scores[key] = calculate_similarity_optimized(qa_text, normalized_whisper_text)
            else:
                scores[key] = 0.0
        
        max_score = max(scores.values()) if scores else 0.0
        
        if max_score > 0.8:
            match_type = max(scores, key=scores.get)
            return {
                'segment': segment,
                'confidence': max_score,
                'match_type': match_type,
                'index': i,
                'scores': scores
            }

        if max_score > best_score:
            best_score = max_score
            match_type = max(scores, key=scores.get)
            best_match = {"segment": segment, "confidence": max_score, "match_type": match_type, "index": i, "scores": scores}

    return best_match

def find_best_whisper_match(qa: Dict, whisper_segments: List[Dict], used_indices: set) -> Dict:
    """単一のQ&Aに対する最適なWhisperセグメントを検索（後方互換性のため）"""
    normalized_whisper_texts = [normalize_for_matching(seg['text']) for seg in whisper_segments]
    return find_best_whisper_match_optimized(qa, whisper_segments, normalized_whisper_texts, used_indices)


def calculate_similarity_optimized(norm_text1: str, norm_text2: str) -> float:
    """2つの正規化済みテキストの類似度を計算（最適化版）"""
    if not norm_text1 or not norm_text2:
        return 0.0
    
    len_ratio = min(len(norm_text1), len(norm_text2)) / max(len(norm_text1), len(norm_text2))
    if len_ratio < 0.1:
        return 0.0
    
    basic_similarity = SequenceMatcher(None, norm_text1, norm_text2).ratio()
    
    if basic_similarity < 0.1:
        return basic_similarity
    
    keyword_bonus = calculate_keyword_bonus(norm_text1, norm_text2)
    
    return min(1.0, basic_similarity + keyword_bonus)

def calculate_similarity(text1: str, text2: str) -> float:
    """2つのテキストの類似度を計算（後方互換性のため）"""
    if not text1 or not text2:
        return 0.0
    
    norm_text1 = normalize_for_matching(text1)
    norm_text2 = normalize_for_matching(text2)
    
    return calculate_similarity_optimized(norm_text1, norm_text2)


def normalize_for_matching(text: str) -> str:
    """マッチング用のテキスト正規化"""
    text = re.sub(r"[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\w]", "", text)
    return text.lower()


def calculate_keyword_bonus(text1: str, text2: str) -> float:
    """重要キーワードの一致によるボーナススコア"""
    keywords1 = set(re.findall(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]{3,}", text1))
    keywords2 = set(re.findall(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]{3,}", text2))

    if not keywords1 or not keywords2:
        return 0.0

    intersection = keywords1.intersection(keywords2)
    union = keywords1.union(keywords2)

    return 0.2 * len(intersection) / len(union) if union else 0.0


def estimate_timing_from_order(qa: Dict, all_qa: List[Dict], matches: List[Dict]) -> Dict:
    """順序に基づいてタイミングを推定（完全重複回避版）"""
    qa_index = next(i for i, q in enumerate(all_qa) if q["id"] == qa["id"])
    video_duration = 1500  # 25分 = 1500秒

    all_used_timings = []
    for match in matches:
        if match.get("whisper_segment"):
            start = max(0, match["whisper_segment"]["start"] - 3)
            end = min(video_duration, match["whisper_segment"]["end"] + 3)
            all_used_timings.append((start, end))
        elif match.get("estimated_timing"):
            all_used_timings.append((
                match["estimated_timing"]["start"], 
                match["estimated_timing"]["end"]
            ))
    
    all_used_timings.sort()

    default_duration = min(15, video_duration / max(len(all_qa), 1))
    
    estimated_start, estimated_end = find_next_available_slot(
        all_used_timings, default_duration, video_duration
    )

    return {"start": estimated_start, "end": estimated_end, "duration": estimated_end - estimated_start}

def find_available_time_slot(preferred_start: float, preferred_end: float, 
                               used_timings: List[tuple], video_duration: float) -> tuple:
    """利用可能な時間スロットを見つける"""
    if not used_timings:
        return preferred_start, preferred_end
    
    duration = preferred_end - preferred_start
    min_duration = max(5, duration)  # 最小5秒
    
    sorted_timings = sorted(used_timings)
    
    if is_time_slot_available(preferred_start, preferred_end, sorted_timings):
        return preferred_start, preferred_end
    
    current_pos = 0
    
    for used_start, used_end in sorted_timings:
        gap_start = current_pos
        gap_end = used_start
        gap_duration = gap_end - gap_start
        
        if gap_duration >= min_duration:
            slot_start = gap_start
            slot_end = min(gap_start + duration, gap_end)
            
            if slot_end - slot_start < min_duration:
                slot_end = slot_start + min_duration
                if slot_end <= gap_end:
                    return slot_start, slot_end
            else:
                return slot_start, slot_end
        
        current_pos = max(current_pos, used_end)
    
    if current_pos < video_duration:
        remaining_duration = video_duration - current_pos
        if remaining_duration >= min_duration:
            slot_start = current_pos
            slot_end = min(current_pos + duration, video_duration)
            
            if slot_end - slot_start < min_duration:
                slot_end = min(slot_start + min_duration, video_duration)
            
            return slot_start, slot_end
    
    fallback_duration = min(min_duration, 10)  # 最大10秒
    fallback_start = max(0, video_duration - fallback_duration)
    fallback_end = video_duration
    
    return fallback_start, fallback_end

def find_non_overlapping_slot(allocated_timings: List[tuple], duration: float, video_duration: float) -> Dict:
    """完全に重複しない時間スロットを見つける"""
    min_duration = max(5, duration)
    sorted_timings = sorted(allocated_timings)
    
    current_pos = 0
    
    for used_start, used_end in sorted_timings:
        available_space = used_start - current_pos
        
        if available_space >= min_duration:
            slot_start = current_pos
            slot_end = min(current_pos + duration, used_start)
            
            if slot_end - slot_start >= min_duration:
                return {"start": slot_start, "end": slot_end, "duration": slot_end - slot_start}
        
        current_pos = max(current_pos, used_end)
    
    remaining_space = video_duration - current_pos
    if remaining_space >= min_duration:
        slot_start = current_pos
        slot_end = min(current_pos + duration, video_duration)
        return {"start": slot_start, "end": slot_end, "duration": slot_end - slot_start}
    
    fallback_duration = min(min_duration, 5)
    fallback_start = max(0, video_duration - fallback_duration)
    fallback_end = video_duration
    
    return {"start": fallback_start, "end": fallback_end, "duration": fallback_end - fallback_start}

def find_next_available_slot(used_timings: List[tuple], duration: float, video_duration: float) -> tuple:
    """次に利用可能な時間スロットを見つける（完全重複回避）"""
    min_duration = max(5, duration)
    sorted_timings = sorted(used_timings)
    
    current_pos = 0
    
    for used_start, used_end in sorted_timings:
        available_space = used_start - current_pos
        
        if available_space >= min_duration:
            slot_start = current_pos
            slot_end = min(current_pos + duration, used_start)
            
            if slot_end - slot_start >= min_duration:
                return slot_start, slot_end
        
        current_pos = max(current_pos, used_end)
    
    remaining_space = video_duration - current_pos
    if remaining_space >= min_duration:
        slot_start = current_pos
        slot_end = min(current_pos + duration, video_duration)
        return slot_start, slot_end
    
    fallback_duration = min(min_duration, 5)
    fallback_start = max(0, video_duration - fallback_duration)
    fallback_end = video_duration
    
    return fallback_start, fallback_end

def is_time_slot_available(start: float, end: float, used_timings: List[tuple]) -> bool:
    """指定された時間スロットが利用可能かチェック"""
    for used_start, used_end in used_timings:
        if not (end <= used_start or start >= used_end):
            return False
    return True
