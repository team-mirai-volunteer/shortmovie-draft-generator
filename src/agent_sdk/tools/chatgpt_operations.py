# -*- coding: utf-8 -*-
"""ChatGPTクライアント操作用ツール"""

from typing import Any, Dict

from agents import RunContextWrapper, function_tool

from ...clients.chatgpt_client import ChatGPTClient, TranscriptionResult
from ..context.youtube_scenario_context import YouTubeScenarioContext


@function_tool
def generate_scenarios_with_chatgpt(context: RunContextWrapper[YouTubeScenarioContext], additional_context: str = "") -> Dict[str, Any]:
    """ChatGPTを使用して企画案を生成する

    Args:
        context: YouTubeScenarioContextのラッパー
        additional_context: 追加のコンテキスト情報

    Returns:
        生成結果
    """
    try:
        youtube_context: YouTubeScenarioContext = context.context

        if not youtube_context.transcript_chunks:
            return {
                "success": False,
                "message": "字幕データが見つかりません。先にget_transcript()を実行してください。",
            }

        transcript_text = youtube_context.get_transcript_text()

        transcription = TranscriptionResult(text=transcript_text, duration=youtube_context.video_duration, language="ja")

        chatgpt_client = ChatGPTClient()
        draft_result = chatgpt_client.generate_draft(transcription, additional_context)

        scenarios = []
        for proposal in draft_result.proposals:
            scenario_dict = {
                "title": proposal.title,
                "description": proposal.summary,
                "first_impact": proposal.first_impact,
                "last_conclusion": proposal.last_conclusion,
                "summary": proposal.summary,
                "target_duration": 60.0,
                "cut_segments": [],
            }
            scenarios.append(scenario_dict)
            youtube_context.add_scenario(scenario_dict)

        return {
            "success": True,
            "message": f"ChatGPTで{len(scenarios)}件の企画案を生成しました",
            "data": {"scenarios": scenarios, "total_count": draft_result.total_count},
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"ChatGPTでの企画案生成に失敗しました: {str(e)}",
        }


@function_tool
def generate_scenarios_from_prompt(
    context: RunContextWrapper[YouTubeScenarioContext],
    prompt: str,
    additional_context: str = "",
) -> Dict[str, Any]:
    """プロンプトからChatGPTを使用して企画案を生成する

    Args:
        context: YouTubeScenarioContextのラッパー
        prompt: 生成プロンプト
        additional_context: 追加のコンテキスト情報

    Returns:
        生成結果
    """
    try:
        youtube_context: YouTubeScenarioContext = context.context

        chatgpt_client = ChatGPTClient()
        draft_result = chatgpt_client.generate_draft_from_prompt(prompt, additional_context)

        scenarios = []
        for proposal in draft_result.proposals:
            scenario_dict = {
                "title": proposal.title,
                "description": proposal.summary,
                "first_impact": proposal.first_impact,
                "last_conclusion": proposal.last_conclusion,
                "summary": proposal.summary,
                "target_duration": 60.0,
                "cut_segments": [],
            }
            scenarios.append(scenario_dict)
            youtube_context.add_scenario(scenario_dict)

        return {
            "success": True,
            "message": f"プロンプトから{len(scenarios)}件の企画案を生成しました",
            "data": {"scenarios": scenarios, "total_count": draft_result.total_count},
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"プロンプトからの企画案生成に失敗しました: {str(e)}",
        }
