from typing import List

from agents import RunResult, RunResultStreaming
from openai.types.responses import ResponseInputItemParam


def create_input_with_history(
    new_user_message: str,
    last_result: RunResult | RunResultStreaming | None,
) -> List[ResponseInputItemParam]:
    """
    OpenAI Agents SDKの推奨方法で会話履歴を含む入力を作成

    Args:
        new_user_message: 新しいユーザーメッセージ
        last_result: 前回のAgent実行結果
        additional_context: 追加のコンテキスト情報（ファイル情報等）

    Returns:
        会話履歴を含む入力リスト
    """
    if last_result and hasattr(last_result, "to_input_list"):
        # 前回の結果から会話履歴を取得し、新しいメッセージを追加
        conversation_history = last_result.to_input_list()
        conversation_history.append({"role": "user", "content": new_user_message})
        return conversation_history
    else:
        # 初回の場合は新しいメッセージのみ
        return [{"role": "user", "content": new_user_message}]
