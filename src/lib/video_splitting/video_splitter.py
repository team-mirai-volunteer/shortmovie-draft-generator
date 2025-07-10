from typing import List, Dict, Any, Optional
import os
import re
from pathlib import Path
from src.lib.youtube.video_processing import create_short_video
from src.agent_sdk.schemas.youtube import CutSegment
from .csv_parser import parse_qa_csv
from .whisper_analyzer import load_whisper_transcript
from .text_matcher import match_qa_with_whisper


class VideoSplitter:
    def __init__(self, source_video_path: str, output_dir: str):
        self.source_video_path = source_video_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def split_video_from_csv_and_whisper(self, csv_path: str, whisper_json_path: str, confidence_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """CSVファイルとWhisper解析結果を基に動画を1問1答形式に分割"""
        print("CSVとWhisperデータを読み込み中...")

        qa_segments = parse_qa_csv(csv_path)
        whisper_segments = load_whisper_transcript(whisper_json_path)

        print(f"Q&Aセグメント数: {len(qa_segments)}")
        print(f"Whisperセグメント数: {len(whisper_segments)}")

        print("テキストマッチングを実行中...")
        matches = match_qa_with_whisper(qa_segments, whisper_segments, confidence_threshold)

        matched_count = sum(1 for m in matches if m["whisper_segment"] is not None)
        print(f"マッチング成功: {matched_count}/{len(matches)} ({matched_count/len(matches)*100:.1f}%)")

        print("動画分割を開始...")
        results = []
        for i, match in enumerate(matches):
            print(f"処理中: {i+1}/{len(matches)} - {match['qa']['query'][:50]}...")
            result = self._create_single_qa_video(match, i + 1)
            results.append(result)

        return results

    def _create_single_qa_video(self, match: Dict[str, Any], index: int) -> Dict[str, Any]:
        """単一のQ&A動画を作成"""
        qa = match["qa"]

        if match["whisper_segment"]:
            start_time = match["whisper_segment"]["start"]
            end_time = match["whisper_segment"]["end"]
            timing_source = "whisper"
        else:
            start_time = match["estimated_timing"]["start"]
            end_time = match["estimated_timing"]["end"]
            timing_source = "estimated"

        cut_segment = CutSegment(
            start_time=start_time,
            end_time=end_time,
            content=f"Q: {qa['query'][:100]}...",
            purpose=f"Q&A #{index}",
            editing_notes=f"質問: {qa['qtext'][:50]}... | 信頼度: {match['confidence']:.2f} | ソース: {timing_source}",
        )

        safe_filename = self._generate_safe_filename(qa, index)
        output_path = self.output_dir / safe_filename

        try:
            cut_segment_dict = {
                "start_time": cut_segment.start_time,
                "end_time": cut_segment.end_time,
                "content": cut_segment.content,
                "purpose": cut_segment.purpose,
                "editing_notes": cut_segment.editing_notes
            }
            
            result = create_short_video(source_video_path=self.source_video_path, cut_segments=[cut_segment_dict], output_path=str(output_path), video_format="mp4", quality="high")

            return {
                "index": index,
                "segment_id": qa["id"],
                "output_path": str(output_path) if result.success else None,
                "success": result.success,
                "error": result.error if hasattr(result, "error") else None,
                "query": qa["query"],
                "duration": end_time - start_time,
                "confidence": match["confidence"],
                "timing_source": timing_source,
                "start_time": start_time,
                "end_time": end_time,
            }
        except Exception as e:
            return {
                "index": index,
                "segment_id": qa["id"],
                "output_path": None,
                "success": False,
                "error": str(e),
                "query": qa["query"],
                "duration": end_time - start_time,
                "confidence": match["confidence"],
                "timing_source": timing_source,
                "start_time": start_time,
                "end_time": end_time,
            }

    def _generate_safe_filename(self, qa: Dict, index: int) -> str:
        """安全なファイル名を生成"""
        safe_query = re.sub(r"[^\w\s-]", "", qa["query"][:30])
        safe_query = re.sub(r"[-\s]+", "-", safe_query).strip("-")

        return f"qa_{index:04d}_{qa['id'][:8]}_{safe_query}.mp4"
