# -*- coding: utf-8 -*-
"""YouTube字幕抽出用ツール"""

from typing import Dict, List, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
import re
from copy import deepcopy


def extract_youtube_transcript(video_id: str, languages: List[str] = ["ja", "ja-JP", "en", "en-US"]) -> Dict[str, Any]:
    """YouTube動画の字幕を抽出する

    Args:
        video_id: YouTube動画ID
        languages: 字幕言語の優先順位リスト

    Returns:
        字幕データを含む辞書
    """
    try:
        # 利用可能な字幕をチェック
        available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

        transcript_list = None
        used_language = None

        # 指定された言語で字幕を取得
        for lang in languages:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                used_language = lang
                break
            except Exception:
                continue

        # 指定言語で取得できない場合、利用可能な任意の言語で取得
        if transcript_list is None:
            try:
                # 自動生成字幕も含めて取得
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                used_language = "auto"
            except Exception as e:
                return {"success": False, "error": f"字幕が見つかりません: {str(e)}", "transcript": None, "language": None, "available_languages": []}

        # 利用可能な言語リストを取得
        available_languages = []
        try:
            for transcript in available_transcripts:
                available_languages.append(
                    {
                        "language": transcript.language,
                        "language_code": transcript.language_code,
                        "is_generated": transcript.is_generated,
                        "is_translatable": transcript.is_translatable,
                    }
                )
        except Exception:
            pass

        return {
            "success": True,
            "error": None,
            "transcript": transcript_list,
            "language": used_language,
            "available_languages": available_languages,
            "total_segments": len(transcript_list) if transcript_list else 0,
        }

    except Exception as e:
        return {"success": False, "error": f"字幕抽出エラー: {str(e)}", "transcript": None, "language": None, "available_languages": []}


def split_transcript_by_sentence(transcript_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """字幕を文章単位で分割する（。で分割）

    Args:
        transcript_chunks: 元の字幕チャンク

    Returns:
        文章単位で分割された字幕チャンク
    """
    result = []

    for entry in transcript_chunks:
        text = entry.get("text", "")
        start = entry.get("start", 0)
        duration = entry.get("duration", 0)

        if "。" in text:
            split_index = text.index("。") + 1  # 「。」の直後で分割
            first_text = text[:split_index]
            second_text = text[split_index:]

            total_len = len(text)
            len_first = len(first_text)
            len_second = len(second_text)

            # durationの比率を文字数ベースで計算
            duration_first = duration * (len_first / total_len) if total_len > 0 else 0
            duration_second = duration - duration_first

            result.append(
                {
                    "text": first_text,
                    "start": start,
                    "duration": round(duration_first, 3),
                }
            )

            if second_text.strip():  # 空文字でない場合のみ追加
                result.append(
                    {
                        "text": second_text,
                        "start": round(start + duration_first, 3),
                        "duration": round(duration_second, 3),
                    }
                )
        else:
            result.append(deepcopy(entry))

    return result


def merge_transcript_until_period(transcript_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """字幕を「。」を基準に結合し、文章単位にする

    Args:
        transcript_chunks: 分割された字幕チャンク

    Returns:
        文章単位に結合された字幕チャンク
    """
    merged = []
    buffer = []

    def flush_buffer():
        if not buffer:
            return
        if len(buffer) == 1:
            merged.append(buffer[0])
        else:
            text = "".join(item["text"] for item in buffer)
            start = buffer[0]["start"]
            duration = sum(item["duration"] for item in buffer)
            merged.append({"text": text, "start": round(start, 3), "duration": round(duration, 3)})
        buffer.clear()

    for chunk in transcript_chunks:
        buffer.append(chunk)
        if chunk.get("text", "").endswith("。"):
            flush_buffer()

    # 残りがあれば最後にflush
    flush_buffer()
    return merged


def fix_transcript_text(transcript_chunks: List[Dict[str, Any]], custom_replacements: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """字幕テキストの自動修正

    Args:
        transcript_chunks: 字幕チャンク
        custom_replacements: カスタム置換辞書

    Returns:
        修正された字幕チャンク
    """
    # デフォルトの置換パターン
    default_replacements = {
        # 一般的な誤変換
        "トレサビリティ": "トレーサビリティ",
        "脳水症": "農水省",
        "ハカソ": "ハッカソン",
        "チーム未来": "チームみらい",
        "安野の高ひ": "安野たかひろ",
        "安野高ひ": "安野たかひろ",
        # フィラー除去パターン
        r"\bあ\b": "",
        r"\bえー\b": "",
        r"\bうー\b": "",
        r"\bんー\b": "",
    }

    # カスタム置換を追加
    if custom_replacements:
        default_replacements.update(custom_replacements)

    result = []

    for chunk in transcript_chunks:
        text = chunk.get("text", "")

        # 置換処理
        for pattern, replacement in default_replacements.items():
            if pattern.startswith("r'") and pattern.endswith("'"):
                # 正規表現パターン
                regex_pattern = pattern[2:-1]  # r'...' の部分を取り出し
                text = re.sub(regex_pattern, replacement, text)
            else:
                # 通常の文字列置換
                text = text.replace(pattern, replacement)

        # 連続する空白を単一に
        text = re.sub(r"\s+", " ", text).strip()

        # 結果に追加
        if text:  # 空文字でない場合のみ
            result.append({"text": text, "start": chunk.get("start", 0), "duration": chunk.get("duration", 0)})

    return result
