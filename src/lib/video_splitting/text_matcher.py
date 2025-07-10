from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher
import re


def match_qa_with_whisper(qa_segments: List[Dict], whisper_segments: List[Dict], confidence_threshold: float = 0.3) -> List[Dict]:
    """Q&AセグメントとWhisperセグメントをマッチング"""
    matches = []
    used_whisper_indices = set()

    for qa in qa_segments:
        best_match = find_best_whisper_match(qa, whisper_segments, used_whisper_indices)

        if best_match and best_match["confidence"] >= confidence_threshold:
            matches.append({"qa": qa, "whisper_segment": best_match["segment"], "confidence": best_match["confidence"], "match_type": best_match["match_type"]})
            used_whisper_indices.add(best_match["index"])
        else:
            estimated_timing = estimate_timing_from_order(qa, qa_segments, matches)
            matches.append({"qa": qa, "whisper_segment": None, "estimated_timing": estimated_timing, "confidence": 0.0, "match_type": "estimated"})

    return matches


def find_best_whisper_match(qa: Dict, whisper_segments: List[Dict], used_indices: set) -> Dict:
    """単一のQ&Aに対する最適なWhisperセグメントを検索"""
    best_match = None
    best_score = 0

    for i, segment in enumerate(whisper_segments):
        if i in used_indices:
            continue

        scores = {
            "qtext": calculate_similarity(qa["qtext"], segment["text"]),
            "text": calculate_similarity(qa["text"], segment["text"]),
            "combined": calculate_similarity(qa["combined_text"], segment["text"]),
            "query": calculate_similarity(qa["query"], segment["text"]),
        }

        max_score = max(scores.values())
        match_type = max(scores, key=scores.get)

        if max_score > best_score:
            best_score = max_score
            best_match = {"segment": segment, "confidence": max_score, "match_type": match_type, "index": i, "scores": scores}

    return best_match


def calculate_similarity(text1: str, text2: str) -> float:
    """2つのテキストの類似度を計算"""
    if not text1 or not text2:
        return 0.0

    norm_text1 = normalize_for_matching(text1)
    norm_text2 = normalize_for_matching(text2)

    basic_similarity = SequenceMatcher(None, norm_text1, norm_text2).ratio()

    keyword_bonus = calculate_keyword_bonus(norm_text1, norm_text2)

    return min(1.0, basic_similarity + keyword_bonus)


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
    """順序に基づいてタイミングを推定"""
    qa_index = next(i for i, q in enumerate(all_qa) if q["id"] == qa["id"])

    prev_match = None
    next_match = None

    for i in range(qa_index - 1, -1, -1):
        match = next((m for m in matches if m["qa"]["id"] == all_qa[i]["id"]), None)
        if match and match["whisper_segment"]:
            prev_match = match
            break

    for i in range(qa_index + 1, len(all_qa)):
        match = next((m for m in matches if m["qa"]["id"] == all_qa[i]["id"]), None)
        if match and match["whisper_segment"]:
            next_match = match
            break

    if prev_match and next_match:
        prev_end = prev_match["whisper_segment"]["end"]
        next_start = next_match["whisper_segment"]["start"]
        estimated_start = prev_end + (next_start - prev_end) * 0.3
        estimated_end = prev_end + (next_start - prev_end) * 0.7
    elif prev_match:
        estimated_start = prev_match["whisper_segment"]["end"]
        estimated_end = estimated_start + 60
    elif next_match:
        estimated_end = next_match["whisper_segment"]["start"]
        estimated_start = max(0, estimated_end - 60)
    else:
        estimated_start = qa_index * 60
        estimated_end = estimated_start + 60

    return {"start": estimated_start, "end": estimated_end, "duration": estimated_end - estimated_start}
