import json
from typing import List, Dict, Any
import re


def load_whisper_transcript(json_path: str) -> List[Dict[str, Any]]:
    """Whisper JSON出力を読み込みセグメントリストを返す"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = []
    if "segments" in data:
        for segment in data["segments"]:
            segments.append(
                {
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": normalize_text(segment.get("text", "")),
                    "duration": segment.get("end", 0) - segment.get("start", 0),
                }
            )

    return segments


def normalize_text(text: str) -> str:
    """テキストを正規化（空白除去、句読点統一など）"""
    text = re.sub(r"\s+", "", text)
    text = text.replace("。", "").replace("、", "").replace("？", "").replace("！", "")
    return text.strip()


def merge_segments_by_duration(segments: List[Dict], max_duration: float = 120.0) -> List[Dict]:
    """短いセグメントを結合して適切な長さにする"""
    merged = []
    current_group = []
    current_duration = 0

    for segment in segments:
        if current_duration + segment["duration"] <= max_duration:
            current_group.append(segment)
            current_duration += segment["duration"]
        else:
            if current_group:
                merged.append(merge_segment_group(current_group))
            current_group = [segment]
            current_duration = segment["duration"]

    if current_group:
        merged.append(merge_segment_group(current_group))

    return merged


def merge_segment_group(segments: List[Dict]) -> Dict:
    """セグメントグループを1つのセグメントに結合"""
    if not segments:
        return {}

    return {"start": segments[0]["start"], "end": segments[-1]["end"], "text": "".join(seg["text"] for seg in segments), "duration": segments[-1]["end"] - segments[0]["start"]}
