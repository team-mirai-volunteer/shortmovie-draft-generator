# -*- coding: utf-8 -*-
"""YouTubeContext操作用ツール"""

from typing import Dict, List, Any, Optional
from agents import function_tool, RunContextWrapper
from ..context.youtube_scenario_context import YouTubeScenarioContext
from ...agent_sdk.schemas.youtube import CutSegment, Scenario


@function_tool
def get_video_info(context: RunContextWrapper[YouTubeScenarioContext]) -> Dict[str, Any]:
    """動画情報を取得する

    Args:
        context: YouTubeScenarioContextのラッパー

    Returns:
        動画情報の辞書
    """
    try:
        youtube_context: YouTubeScenarioContext = context.context

        # オブジェクト型の場合の処理
        video_info = {
            "video_id": youtube_context.video_id,
            "title": youtube_context.video_title,
            "description": youtube_context.video_description,
            "duration": youtube_context.video_duration,
            "duration_string": youtube_context.video_duration_string,
            "uploader": youtube_context.channel_name,
            "upload_date": youtube_context.upload_date,
            "view_count": youtube_context.view_count,
            "like_count": youtube_context.like_count,
            "thumbnail": youtube_context.thumbnail,
            "webpage_url": youtube_context.video_url,
            "tags": youtube_context.tags,
            "categories": youtube_context.categories,
            "availability": youtube_context.availability,
            "age_limit": youtube_context.age_limit,
        }

        return {"success": True, "message": "動画情報を取得しました", "data": video_info}
    except Exception as e:
        return {"success": False, "message": f"動画情報の取得に失敗しました: {str(e)}"}


@function_tool
def get_transcript(context: RunContextWrapper[YouTubeScenarioContext]) -> Dict[str, Any]:
    """字幕データを取得する

    Args:
        context: YouTubeScenarioContextのラッパー

    Returns:
        字幕データの辞書
    """
    try:
        youtube_context: YouTubeScenarioContext = context.context

        # 生のtranscript_chunksを優先的に提供（タイムスタンプの精度が高い）
        transcript_data = {
            "transcript_chunks": youtube_context.transcript_chunks,
            "transcript_text": " ".join([chunk.get("text", "") for chunk in youtube_context.transcript_chunks]),
            "is_extracted": youtube_context.is_transcript_extracted,
            "chunks_count": len(youtube_context.transcript_chunks),
            "note": "transcript_chunksを使用してください（より正確なタイムスタンプ）",
        }

        return {"success": True, "message": f"字幕データを取得しました（{len(youtube_context.transcript_chunks)}チャンク）", "data": transcript_data}
    except Exception as e:
        return {"success": False, "message": f"字幕データの取得に失敗しました: {str(e)}"}


@function_tool
def get_scenarios(context: RunContextWrapper[YouTubeScenarioContext]) -> Dict[str, Any]:
    """現在の企画案を取得する

    Args:
        context: YouTubeScenarioContextのラッパー

    Returns:
        企画案リストの辞書
    """
    try:
        youtube_context: YouTubeScenarioContext = context.context

        scenarios_data = {
            "generated_scenarios": youtube_context.generated_scenarios,
            "selected_scenarios": youtube_context.selected_scenarios,
            "scenarios_count": len(youtube_context.generated_scenarios),
            "is_generated": youtube_context.is_scenarios_generated,
        }

        return {"success": True, "message": f"企画案を取得しました（{len(youtube_context.generated_scenarios)}件）", "data": scenarios_data}
    except Exception as e:
        return {"success": False, "message": f"企画案の取得に失敗しました: {str(e)}"}


@function_tool
def add_scenario(context: RunContextWrapper[YouTubeScenarioContext], scenario: Scenario) -> Dict[str, Any]:
    """新しい企画案を追加する

    Args:
        context: YouTubeScenarioContextのラッパー
        scenario: 追加する企画案

    Returns:
        追加結果
    """
    try:
        youtube_context: YouTubeScenarioContext = context.context
        scenario_dict = scenario.dict()
        youtube_context.add_scenario(scenario_dict)

        return {
            "success": True,
            "message": f"企画案「{scenario.title}」を追加しました",
            "data": {"scenario": scenario_dict, "total_scenarios": len(youtube_context.generated_scenarios)},
        }
    except Exception as e:
        return {"success": False, "message": f"企画案の追加に失敗しました: {str(e)}"}


@function_tool
def update_scenario(context: RunContextWrapper[YouTubeScenarioContext], index: int, scenario: Scenario) -> Dict[str, Any]:
    """既存の企画案を更新する

    Args:
        context: YouTubeScenarioContextのラッパー
        index: 更新する企画案のインデックス
        scenario: 更新後の企画案

    Returns:
        更新結果
    """
    try:
        youtube_context: YouTubeScenarioContext = context.context

        if 0 <= index < len(youtube_context.generated_scenarios):
            scenario_dict = scenario.dict()
            youtube_context.generated_scenarios[index] = scenario_dict
            youtube_context.update_timestamp()

            return {"success": True, "message": f"企画案[{index}]「{scenario.title}」を更新しました", "data": {"index": index, "scenario": scenario_dict}}
        else:
            return {"success": False, "message": f"インデックス{index}は範囲外です（0-{len(youtube_context.generated_scenarios)-1}）"}
    except Exception as e:
        return {"success": False, "message": f"企画案の更新に失敗しました: {str(e)}"}


@function_tool
def delete_scenario(context: RunContextWrapper[YouTubeScenarioContext], index: int) -> Dict[str, Any]:
    """企画案を削除する

    Args:
        context: YouTubeScenarioContextのラッパー
        index: 削除する企画案のインデックス

    Returns:
        削除結果
    """
    try:
        youtube_context: YouTubeScenarioContext = context.context

        if 0 <= index < len(youtube_context.generated_scenarios):
            deleted_scenario = youtube_context.generated_scenarios.pop(index)
            youtube_context.update_timestamp()

            return {
                "success": True,
                "message": f"企画案[{index}]「{deleted_scenario.get('title', '')}」を削除しました",
                "data": {"deleted_scenario": deleted_scenario, "remaining_count": len(youtube_context.generated_scenarios)},
            }
        else:
            return {"success": False, "message": f"インデックス{index}は範囲外です（0-{len(youtube_context.generated_scenarios)-1}）"}
    except Exception as e:
        return {"success": False, "message": f"企画案の削除に失敗しました: {str(e)}"}


@function_tool
def get_cut_segments(context: RunContextWrapper[YouTubeScenarioContext]) -> Dict[str, Any]:
    """現在のカットセグメントを取得する

    Args:
        context: YouTubeScenarioContextのラッパー

    Returns:
        カットセグメントリストの辞書
    """
    try:
        youtube_context: YouTubeScenarioContext = context.context

        cut_segments_data = {"cut_segments": youtube_context.cut_segments, "segments_count": len(youtube_context.cut_segments), "is_generated": youtube_context.is_cuts_generated}

        return {"success": True, "message": f"カットセグメントを取得しました（{len(youtube_context.cut_segments)}セグメント）", "data": cut_segments_data}
    except Exception as e:
        return {"success": False, "message": f"カットセグメントの取得に失敗しました: {str(e)}"}


@function_tool
def add_cut_segment(context: RunContextWrapper[YouTubeScenarioContext], segment: CutSegment) -> Dict[str, Any]:
    """新しいカットセグメントを追加する

    Args:
        context: YouTubeScenarioContextのラッパー
        segment: 追加するカットセグメント

    Returns:
        追加結果
    """
    try:
        youtube_context = context.context
        segment_dict = segment.dict()
        youtube_context.cut_segments.append(segment_dict)
        youtube_context.update_timestamp()

        return {
            "success": True,
            "message": f"カットセグメント({segment.start_time:.1f}s-{segment.end_time:.1f}s)を追加しました",
            "data": {"segment": segment_dict, "total_segments": len(youtube_context.cut_segments)},
        }
    except Exception as e:
        return {"success": False, "message": f"カットセグメントの追加に失敗しました: {str(e)}"}


@function_tool
def update_cut_segment(context: RunContextWrapper[YouTubeScenarioContext], index: int, segment: CutSegment) -> Dict[str, Any]:
    """既存のカットセグメントを更新する

    Args:
        context: YouTubeScenarioContextのラッパー
        index: 更新するカットセグメントのインデックス
        segment: 更新後のカットセグメント

    Returns:
        更新結果
    """
    try:
        youtube_context = context.context

        if 0 <= index < len(youtube_context.cut_segments):
            segment_dict = segment.dict()
            youtube_context.cut_segments[index] = segment_dict
            youtube_context.update_timestamp()

            return {
                "success": True,
                "message": f"カットセグメント[{index}]({segment.start_time:.1f}s-{segment.end_time:.1f}s)を更新しました",
                "data": {"index": index, "segment": segment_dict},
            }
        else:
            return {"success": False, "message": f"インデックス{index}は範囲外です（0-{len(youtube_context.cut_segments)-1}）"}
    except Exception as e:
        return {"success": False, "message": f"カットセグメントの更新に失敗しました: {str(e)}"}


@function_tool
def delete_cut_segment(context: RunContextWrapper[YouTubeScenarioContext], index: int) -> Dict[str, Any]:
    """カットセグメントを削除する

    Args:
        context: YouTubeScenarioContextのラッパー
        index: 削除するカットセグメントのインデックス

    Returns:
        削除結果
    """
    try:
        youtube_context = context.context

        if 0 <= index < len(youtube_context.cut_segments):
            deleted_segment = youtube_context.cut_segments.pop(index)
            youtube_context.update_timestamp()

            return {
                "success": True,
                "message": f"カットセグメント[{index}]を削除しました",
                "data": {"deleted_segment": deleted_segment, "remaining_count": len(youtube_context.cut_segments)},
            }
        else:
            return {"success": False, "message": f"インデックス{index}は範囲外です（0-{len(youtube_context.cut_segments)-1}）"}
    except Exception as e:
        return {"success": False, "message": f"カットセグメントの削除に失敗しました: {str(e)}"}


@function_tool
def clear_scenarios(context: RunContextWrapper[YouTubeScenarioContext]) -> Dict[str, Any]:
    """全ての企画案をクリアする

    Args:
        context: YouTubeScenarioContextのラッパー

    Returns:
        クリア結果
    """
    try:
        youtube_context = context.context
        cleared_count = len(youtube_context.generated_scenarios)
        youtube_context.generated_scenarios.clear()
        youtube_context.selected_scenarios.clear()
        youtube_context.is_scenarios_generated = False
        youtube_context.update_timestamp()

        return {"success": True, "message": f"全ての企画案をクリアしました（{cleared_count}件削除）", "data": {"cleared_count": cleared_count}}
    except Exception as e:
        return {"success": False, "message": f"企画案のクリアに失敗しました: {str(e)}"}


@function_tool
def clear_cut_segments(context: RunContextWrapper[YouTubeScenarioContext]) -> Dict[str, Any]:
    """全てのカットセグメントをクリアする

    Args:
        context: YouTubeScenarioContextのラッパー

    Returns:
        クリア結果
    """
    try:
        youtube_context = context.context
        cleared_count = len(youtube_context.cut_segments)
        youtube_context.cut_segments.clear()
        youtube_context.is_cuts_generated = False
        youtube_context.update_timestamp()

        return {"success": True, "message": f"全てのカットセグメントをクリアしました（{cleared_count}セグメント削除）", "data": {"cleared_count": cleared_count}}
    except Exception as e:
        return {"success": False, "message": f"カットセグメントのクリアに失敗しました: {str(e)}"}
