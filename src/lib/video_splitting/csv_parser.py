import pandas as pd
import re
from typing import List, Dict, Any
from datetime import datetime


def parse_qa_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Q&A CSVファイルを解析してセグメント情報を抽出"""
    df = pd.read_csv(csv_path)
    qa_segments = []

    for _, row in df.iterrows():
        if pd.isna(row["answer"]):
            continue

        answer_data = parse_answer_field(row["answer"])

        if is_valid_answer(answer_data):
            segment = {
                "id": row["id"],
                "query": row["query"],
                "created_at": row["created_at"],
                "qtext": answer_data.get("qtext", ""),
                "text": answer_data.get("text", ""),
                "combined_text": f"{answer_data.get('qtext', '')} {answer_data.get('text', '')}",
            }
            qa_segments.append(segment)

    qa_segments.sort(key=lambda x: x["created_at"])
    return qa_segments


def parse_answer_field(answer_text: str) -> Dict[str, str]:
    """answerフィールドから構造化データを抽出"""
    result = {}

    qtext_match = re.search(r"qtext:\s*(.+?)(?=\nqvoice:|$)", answer_text, re.DOTALL)
    if qtext_match:
        result["qtext"] = qtext_match.group(1).strip()

    text_matches = re.findall(r"text:([^\n]+)", answer_text)
    if text_matches:
        result["text"] = " ".join(text_matches)

    return result


def is_valid_answer(answer_data: Dict[str, str]) -> bool:
    """有効な回答かどうかを判定（「回答できません」などを除外）"""
    qtext = answer_data.get("qtext", "").strip()
    text = answer_data.get("text", "").strip()

    invalid_patterns = ["回答できません", "答えられません", "お答えできません", "分かりません", "わかりません", "不明です", "すみません", "申し訳ありません"]

    combined_text = f"{qtext} {text}".lower()

    for pattern in invalid_patterns:
        if pattern in combined_text:
            return False

    if len(qtext) < 5 and len(text) < 5:
        return False

    return True
