# -*- coding: utf-8 -*-
"""YouTube動画処理専用のStreamlitHooksクラス"""

from datetime import datetime
import streamlit as st
from typing import Dict, Any, List
import json

from agents.lifecycle import AgentHooks
from src.agent_sdk.hooks.streamlit_hooks import StreamlitAgentHooks
from src.agent_sdk.tools.display_utils import display_generic_tool_result, display_tool_start
from src.streamlit.functions.state import get_page_state, set_page_state


class YouTubeAgentHooks(StreamlitAgentHooks):
    """YouTube動画処理専用のStreamlitHooksクラス"""

    def __init__(self):
        super().__init__()
        self.agent_display_name = "YouTube動画処理"
        self.icon = "🎬"

    async def on_tool_end(self, context, agent, tool, result):
        """YouTube関連ツールの結果フォーマット"""
        html_contents = None

        # Context操作ツールの処理
        if tool.name in ["get_video_info", "get_transcript", "get_scenarios", "get_cut_segments"]:
            html_contents = self.handle_context_get_operation(context, tool, result)
        elif tool.name in ["add_scenario", "update_scenario", "delete_scenario", "clear_scenarios"]:
            html_contents = self.handle_scenario_operation(context, tool, result)
        elif tool.name in ["add_cut_segment", "update_cut_segment", "delete_cut_segment", "clear_cut_segments"]:
            html_contents = self.handle_cut_segment_operation(context, tool, result)
        # 従来のツール
        elif tool.name == "download_youtube_video":
            html_contents = self.format_video_download_result(result)
        elif tool.name == "extract_youtube_transcript":
            html_contents = self.format_transcript_result(result)
        elif tool.name == "process_transcript_complete":
            html_contents = self.format_processed_transcript_result(result)
        elif tool.name == "generate_short_scenarios":
            html_contents = self.format_scenarios_result(result)
        elif tool.name == "create_short_video":
            html_contents = self.format_video_creation_result(result)
        elif tool.name == "create_subtitle_file":
            html_contents = self.format_subtitle_creation_result(result)
        elif tool.name == "validate_cut_segments":
            html_contents = self.format_validation_result(result)

        # フォールバック処理
        if html_contents is None:
            html_contents = display_generic_tool_result(result, tool.name)

        # 履歴保存と表示
        await self.save_and_display_result(tool, result, html_contents)

    async def save_and_display_result(self, tool, result, html_contents):
        """結果を履歴に保存して表示"""
        messages_history = get_page_state("messages_history", [])
        tool_end_entry = {
            "type": "tool_end",
            "session_id": self.current_session_id,
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool.name,
            "result": str(result)[:1000] if result else "No result",
            "html_contents": html_contents,
            "agent_name": getattr(tool, "agent_name", self.agent_display_name),
        }
        messages_history.append(tool_end_entry)
        set_page_state("messages_history", messages_history)

        st.markdown(html_contents, unsafe_allow_html=True)

    def format_video_download_result(self, result: Dict[str, Any]) -> str:
        """動画ダウンロード結果のフォーマット"""
        if not result.get("success", False):
            return f"""
            <div style="background-color: #ffebee; border: 1px solid #f44336; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <h4 style="color: #d32f2f; margin: 0 0 10px 0;">🚫 動画ダウンロード失敗</h4>
                <p style="margin: 0; color: #d32f2f;"><strong>エラー:</strong> {result.get('error', '不明なエラー')}</p>
            </div>
            """

        metadata = result.get("metadata", {})

        return f"""
        <div style="background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 4px; padding: 15px; margin: 10px 0;">
            <h4 style="color: #2e7d32; margin: 0 0 15px 0;">✅ 動画ダウンロード完了</h4>
            
            <div style="margin-bottom: 10px;">
                <strong>📹 動画情報:</strong>
                <ul style="margin: 5px 0 0 20px;">
                    <li><strong>タイトル:</strong> {metadata.get('title', 'N/A')}</li>
                    <li><strong>チャンネル:</strong> {metadata.get('uploader', 'N/A')}</li>
                    <li><strong>動画長:</strong> {metadata.get('duration', 0) // 60}分{metadata.get('duration', 0) % 60:02d}秒</li>
                    <li><strong>再生回数:</strong> {metadata.get('view_count', 0):,}回</li>
                </ul>
            </div>
            
            <div style="margin-bottom: 10px;">
                <strong>📁 ファイル情報:</strong>
                <ul style="margin: 5px 0 0 20px;">
                    <li><strong>動画ID:</strong> {result.get('video_id', 'N/A')}</li>
                    <li><strong>動画ファイル:</strong> {'✅' if result.get('video_path') else '❌'}</li>
                    <li><strong>音声ファイル:</strong> {'✅' if result.get('audio_path') else '❌'}</li>
                </ul>
            </div>
        </div>
        """

    def format_video_info_result(self, result: Dict[str, Any]) -> str:
        """動画情報取得結果のフォーマット"""
        if not result.get("success", False):
            return f"""
            <div style="background-color: #ffebee; border: 1px solid #f44336; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <h4 style="color: #d32f2f; margin: 0 0 10px 0;">🚫 動画情報取得失敗</h4>
                <p style="margin: 0; color: #d32f2f;"><strong>エラー:</strong> {result.get('error', '不明なエラー')}</p>
            </div>
            """

        video_info = result.get("video_info", {})

        return f"""
        <div style="background-color: #e3f2fd; border: 1px solid #2196f3; border-radius: 4px; padding: 15px; margin: 10px 0;">
            <h4 style="color: #1976d2; margin: 0 0 15px 0;">📋 動画情報</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>
                    <strong>基本情報:</strong>
                    <ul style="margin: 5px 0 0 20px; font-size: 14px;">
                        <li><strong>タイトル:</strong> {video_info.get('title', 'N/A')[:50]}...</li>
                        <li><strong>チャンネル:</strong> {video_info.get('uploader', 'N/A')}</li>
                        <li><strong>動画長:</strong> {video_info.get('duration_string', 'N/A')}</li>
                        <li><strong>投稿日:</strong> {video_info.get('upload_date', 'N/A')}</li>
                    </ul>
                </div>
                <div>
                    <strong>統計情報:</strong>
                    <ul style="margin: 5px 0 0 20px; font-size: 14px;">
                        <li><strong>再生回数:</strong> {video_info.get('view_count', 0):,}回</li>
                        <li><strong>いいね数:</strong> {video_info.get('like_count', 0):,}</li>
                        <li><strong>年齢制限:</strong> {video_info.get('age_limit', 0)}歳以上</li>
                        <li><strong>利用可能性:</strong> {video_info.get('availability', 'N/A')}</li>
                    </ul>
                </div>
            </div>
        </div>
        """

    def format_transcript_result(self, result: Dict[str, Any]) -> str:
        """字幕抽出結果のフォーマット"""
        if not result.get("success", False):
            return f"""
            <div style="background-color: #ffebee; border: 1px solid #f44336; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <h4 style="color: #d32f2f; margin: 0 0 10px 0;">🚫 字幕抽出失敗</h4>
                <p style="margin: 0; color: #d32f2f;"><strong>エラー:</strong> {result.get('error', '不明なエラー')}</p>
            </div>
            """

        available_languages = result.get("available_languages", [])

        return f"""
        <div style="background-color: #f3e5f5; border: 1px solid #9c27b0; border-radius: 4px; padding: 15px; margin: 10px 0;">
            <h4 style="color: #7b1fa2; margin: 0 0 15px 0;">📝 字幕抽出完了</h4>
            
            <div style="margin-bottom: 10px;">
                <strong>抽出結果:</strong>
                <ul style="margin: 5px 0 0 20px;">
                    <li><strong>使用言語:</strong> {result.get('language', 'N/A')}</li>
                    <li><strong>セグメント数:</strong> {result.get('total_segments', 0):,}</li>
                </ul>
            </div>
            
            <div style="margin-bottom: 10px;">
                <strong>利用可能な言語:</strong>
                <div style="margin: 5px 0 0 20px; font-size: 12px;">
                    {', '.join([f"{lang.get('language', 'N/A')} ({'自動生成' if lang.get('is_generated') else '手動'})" for lang in available_languages[:5]])}
                </div>
            </div>
        </div>
        """

    def format_processed_transcript_result(self, result: Dict[str, Any]) -> str:
        """処理済み字幕結果のフォーマット"""
        if not result.get("success", False):
            return f"""
            <div style="background-color: #ffebee; border: 1px solid #f44336; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <h4 style="color: #d32f2f; margin: 0 0 10px 0;">🚫 字幕処理失敗</h4>
                <p style="margin: 0; color: #d32f2f;"><strong>エラー:</strong> {result.get('error', '不明なエラー')}</p>
            </div>
            """

        statistics = result.get("statistics", {})
        processing_steps = result.get("processing_steps", {})

        return f"""
        <div style="background-color: #f3e5f5; border: 1px solid #9c27b0; border-radius: 4px; padding: 15px; margin: 10px 0;">
            <h4 style="color: #7b1fa2; margin: 0 0 15px 0;">🔧 字幕処理完了</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <strong>処理統計:</strong>
                    <ul style="margin: 5px 0 0 20px; font-size: 14px;">
                        <li><strong>元セグメント数:</strong> {statistics.get('original_segments', 0):,}</li>
                        <li><strong>処理後セグメント数:</strong> {statistics.get('processed_segments', 0):,}</li>
                        <li><strong>総時間:</strong> {statistics.get('total_duration', 0):.1f}秒</li>
                    </ul>
                </div>
                <div>
                    <strong>処理内容:</strong>
                    <ul style="margin: 5px 0 0 20px; font-size: 14px;">
                        <li><strong>テキスト修正:</strong> {'✅' if processing_steps.get('text_fixed') else '❌'}</li>
                        <li><strong>文章結合:</strong> {'✅' if processing_steps.get('sentences_merged') else '❌'}</li>
                        <li><strong>カスタム置換:</strong> {'✅' if processing_steps.get('custom_replacements_applied') else '❌'}</li>
                    </ul>
                </div>
            </div>
        </div>
        """

    def format_scenarios_result(self, result: Dict[str, Any]) -> str:
        """シナリオ生成結果のフォーマット"""
        if not result.get("success", False):
            return f"""
            <div style="background-color: #ffebee; border: 1px solid #f44336; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <h4 style="color: #d32f2f; margin: 0 0 10px 0;">🚫 シナリオ生成失敗</h4>
                <p style="margin: 0; color: #d32f2f;"><strong>エラー:</strong> {result.get('error', '不明なエラー')}</p>
            </div>
            """

        scenarios = result.get("scenarios", [])
        generation_info = result.get("generation_info", {})

        scenarios_html = ""
        for i, scenario in enumerate(scenarios[:3], 1):  # 最初の3つのみ表示
            scenarios_html += f"""
            <div style="background-color: #fafafa; border-left: 3px solid #ff9800; padding: 10px; margin: 5px 0;">
                <h5 style="margin: 0 0 5px 0; color: #f57c00;">#{i} {scenario.get('title', 'タイトルなし')}</h5>
                <p style="margin: 0 0 5px 0; font-size: 12px;"><strong>インパクト:</strong> {scenario.get('first_impact', 'N/A')}</p>
                <p style="margin: 0 0 5px 0; font-size: 12px;"><strong>ターゲット:</strong> {scenario.get('target_audience', 'N/A')}</p>
                <p style="margin: 0; font-size: 12px;"><strong>戦略:</strong> {scenario.get('hook_strategy', 'N/A')}</p>
            </div>
            """

        return f"""
        <div style="background-color: #fff3e0; border: 1px solid #ff9800; border-radius: 4px; padding: 15px; margin: 10px 0;">
            <h4 style="color: #f57c00; margin: 0 0 15px 0;">💡 シナリオ生成完了</h4>
            
            <div style="margin-bottom: 15px;">
                <strong>生成情報:</strong>
                <ul style="margin: 5px 0 0 20px; font-size: 14px;">
                    <li><strong>生成数:</strong> {generation_info.get('num_scenarios_generated', 0)}</li>
                    <li><strong>目標時間:</strong> {generation_info.get('target_duration', 0)}秒</li>
                    <li><strong>使用モデル:</strong> {generation_info.get('model_used', 'N/A')}</li>
                </ul>
            </div>
            
            <div>
                <strong>生成されたシナリオ（上位3件）:</strong>
                {scenarios_html}
                {f'<p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">...他{len(scenarios) - 3}件</p>' if len(scenarios) > 3 else ''}
            </div>
        </div>
        """

    def format_cut_segments_result(self, result: Dict[str, Any]) -> str:
        """カットセグメント生成結果のフォーマット"""
        if not result.get("success", False):
            return f"""
            <div style="background-color: #ffebee; border: 1px solid #f44336; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <h4 style="color: #d32f2f; margin: 0 0 10px 0;">🚫 カットセグメント生成失敗</h4>
                <p style="margin: 0; color: #d32f2f;"><strong>エラー:</strong> {result.get('error', '不明なエラー')}</p>
            </div>
            """

        cut_segments = result.get("cut_segments", [])
        generation_info = result.get("generation_info", {})

        segments_html = ""
        for i, segment in enumerate(cut_segments, 1):
            duration = segment.get("end_time", 0) - segment.get("start_time", 0)
            segments_html += f"""
            <div style="background-color: #fafafa; border-left: 3px solid #4caf50; padding: 8px; margin: 3px 0; font-size: 12px;">
                <strong>#{i}</strong> {segment.get('start_time', 0):.1f}s - {segment.get('end_time', 0):.1f}s ({duration:.1f}s)
                <br><em>{segment.get('content', 'N/A')[:100]}...</em>
                <br><span style="color: #666;">目的: {segment.get('purpose', 'N/A')}</span>
            </div>
            """

        return f"""
        <div style="background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 4px; padding: 15px; margin: 10px 0;">
            <h4 style="color: #2e7d32; margin: 0 0 15px 0;">✂️ カットセグメント生成完了</h4>
            
            <div style="margin-bottom: 15px;">
                <strong>生成情報:</strong>
                <ul style="margin: 5px 0 0 20px; font-size: 14px;">
                    <li><strong>セグメント数:</strong> {generation_info.get('num_segments', 0)}</li>
                    <li><strong>総時間:</strong> {generation_info.get('actual_duration', 0):.1f}秒</li>
                    <li><strong>対象シナリオ:</strong> {generation_info.get('scenario_title', 'N/A')}</li>
                </ul>
            </div>
            
            <div>
                <strong>カットセグメント:</strong>
                <div style="max-height: 200px; overflow-y: auto; margin-top: 5px;">
                    {segments_html}
                </div>
            </div>
        </div>
        """

    def format_video_creation_result(self, result: Dict[str, Any]) -> str:
        """動画作成結果のフォーマット"""
        if not result.get("success", False):
            return f"""
            <div style="background-color: #ffebee; border: 1px solid #f44336; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <h4 style="color: #d32f2f; margin: 0 0 10px 0;">🚫 動画作成失敗</h4>
                <p style="margin: 0; color: #d32f2f;"><strong>エラー:</strong> {result.get('error', '不明なエラー')}</p>
            </div>
            """

        video_info = result.get("video_info", {})
        processing_details = result.get("processing_details", {})

        return f"""
        <div style="background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 4px; padding: 15px; margin: 10px 0;">
            <h4 style="color: #2e7d32; margin: 0 0 15px 0;">🎬 動画作成完了</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <strong>作成結果:</strong>
                    <ul style="margin: 5px 0 0 20px; font-size: 14px;">
                        <li><strong>出力ファイル:</strong> ✅ 作成済み</li>
                        <li><strong>処理セグメント数:</strong> {result.get('segments_processed', 0)}</li>
                        <li><strong>動画時間:</strong> {video_info.get('duration', 0):.1f}秒</li>
                        <li><strong>ファイルサイズ:</strong> {video_info.get('size', 0) / 1024 / 1024:.1f}MB</li>
                    </ul>
                </div>
                <div>
                    <strong>処理オプション:</strong>
                    <ul style="margin: 5px 0 0 20px; font-size: 14px;">
                        <li><strong>字幕追加:</strong> {'✅' if processing_details.get('subtitle_added') else '❌'}</li>
                        <li><strong>BGM追加:</strong> {'✅' if processing_details.get('bgm_added') else '❌'}</li>
                        <li><strong>フォーマット:</strong> {processing_details.get('format', 'N/A')}</li>
                        <li><strong>品質:</strong> {processing_details.get('quality', 'N/A')}</li>
                    </ul>
                </div>
            </div>
            
            <div style="margin-top: 10px; padding: 10px; background-color: #f0f8f0; border-radius: 4px;">
                <strong>📁 出力ファイル:</strong> {result.get('output_path', 'N/A')}
            </div>
        </div>
        """

    def format_subtitle_creation_result(self, result: Dict[str, Any]) -> str:
        """字幕ファイル作成結果のフォーマット"""
        if not result.get("success", False):
            return f"""
            <div style="background-color: #ffebee; border: 1px solid #f44336; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <h4 style="color: #d32f2f; margin: 0 0 10px 0;">🚫 字幕ファイル作成失敗</h4>
                <p style="margin: 0; color: #d32f2f;"><strong>エラー:</strong> {result.get('error', '不明なエラー')}</p>
            </div>
            """

        return f"""
        <div style="background-color: #f3e5f5; border: 1px solid #9c27b0; border-radius: 4px; padding: 15px; margin: 10px 0;">
            <h4 style="color: #7b1fa2; margin: 0 0 15px 0;">📝 字幕ファイル作成完了</h4>
            
            <div style="margin-bottom: 10px;">
                <strong>作成結果:</strong>
                <ul style="margin: 5px 0 0 20px; font-size: 14px;">
                    <li><strong>フォーマット:</strong> {result.get('format', 'N/A').upper()}</li>
                    <li><strong>字幕数:</strong> {result.get('subtitle_count', 0)}</li>
                    <li><strong>出力ファイル:</strong> {result.get('subtitle_path', 'N/A')}</li>
                </ul>
            </div>
        </div>
        """

    def format_validation_result(self, result: Dict[str, Any]) -> str:
        """検証結果のフォーマット"""
        is_valid = result.get("is_valid", False)
        errors = result.get("errors", [])
        warnings = result.get("warnings", [])

        if is_valid and not warnings:
            return f"""
            <div style="background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 4px; padding: 15px; margin: 10px 0;">
                <h4 style="color: #2e7d32; margin: 0 0 15px 0;">✅ 検証成功</h4>
                <p style="margin: 0; color: #2e7d32;">
                    セグメント数: {result.get('num_segments', 0)}, 
                    総時間: {result.get('total_duration', 0):.1f}秒
                </p>
            </div>
            """

        status_color = "#f44336" if not is_valid else "#ff9800"
        status_bg = "#ffebee" if not is_valid else "#fff3e0"
        status_icon = "🚫" if not is_valid else "⚠️"
        status_text = "検証失敗" if not is_valid else "検証警告"

        issues_html = ""
        if errors:
            issues_html += "<div style='margin-bottom: 10px;'><strong>エラー:</strong><ul style='margin: 5px 0 0 20px; color: #d32f2f;'>"
            for error in errors:
                issues_html += f"<li>{error}</li>"
            issues_html += "</ul></div>"

        if warnings:
            issues_html += "<div><strong>警告:</strong><ul style='margin: 5px 0 0 20px; color: #f57c00;'>"
            for warning in warnings:
                issues_html += f"<li>{warning}</li>"
            issues_html += "</ul></div>"

        return f"""
        <div style="background-color: {status_bg}; border: 1px solid {status_color}; border-radius: 4px; padding: 15px; margin: 10px 0;">
            <h4 style="color: {status_color}; margin: 0 0 15px 0;">{status_icon} {status_text}</h4>
            
            <div style="margin-bottom: 10px;">
                <strong>基本情報:</strong>
                <ul style="margin: 5px 0 0 20px; font-size: 14px;">
                    <li><strong>セグメント数:</strong> {result.get('num_segments', 0)}</li>
                    <li><strong>総時間:</strong> {result.get('total_duration', 0):.1f}秒</li>
                </ul>
            </div>
            
            {issues_html}
        </div>
        """

    def handle_context_get_operation(self, context, tool, result):
        """Context取得操作の処理"""
        youtube_context = getattr(context, "youtube_context", None) if context else None
        action = result.get("action", "")

        if action == "get_video_info" and youtube_context:
            return f"""
            <div style="background-color: #e3f2fd; border: 1px solid #2196f3; border-radius: 4px; padding: 15px; margin: 10px 0;">
                <h4 style="color: #1976d2; margin: 0 0 15px 0;">📋 動画情報取得</h4>
                <div style="font-size: 14px;">
                    <p><strong>タイトル:</strong> {youtube_context.video_title}</p>
                    <p><strong>時間:</strong> {youtube_context.video_duration}秒</p>
                    <p><strong>チャンネル:</strong> {youtube_context.channel_name}</p>
                </div>
            </div>
            """
        elif action == "get_transcript" and youtube_context:
            transcript_count = len(youtube_context.transcript_chunks)
            return f"""
            <div style="background-color: #f3e5f5; border: 1px solid #9c27b0; border-radius: 4px; padding: 15px; margin: 10px 0;">
                <h4 style="color: #7b1fa2; margin: 0 0 15px 0;">📝 字幕データ取得</h4>
                <p style="font-size: 14px;"><strong>字幕チャンク数:</strong> {transcript_count}</p>
            </div>
            """
        elif action == "get_scenarios" and youtube_context:
            scenario_count = len(youtube_context.generated_scenarios)
            return f"""
            <div style="background-color: #fff3e0; border: 1px solid #ff9800; border-radius: 4px; padding: 15px; margin: 10px 0;">
                <h4 style="color: #f57c00; margin: 0 0 15px 0;">💡 企画案取得</h4>
                <p style="font-size: 14px;"><strong>企画案数:</strong> {scenario_count}</p>
            </div>
            """

        return display_generic_tool_result(result, tool.name)

    def handle_scenario_operation(self, context, tool, result):
        """企画案操作の処理"""
        youtube_context = getattr(context, "youtube_context", None) if context else None
        action = result.get("action", "")

        if action == "add_scenario" and youtube_context:
            scenario_data = result.get("scenario", {})
            # Contextに実際に追加
            youtube_context.generated_scenarios.append(scenario_data)
            youtube_context.is_scenarios_generated = True
            youtube_context.update_timestamp()

            return f"""
            <div style="background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 4px; padding: 15px; margin: 10px 0;">
                <h4 style="color: #2e7d32; margin: 0 0 15px 0;">✅ 企画案追加</h4>
                <p style="font-size: 14px;"><strong>タイトル:</strong> {scenario_data.get('title', 'N/A')}</p>
                <p style="font-size: 14px;"><strong>総企画案数:</strong> {len(youtube_context.generated_scenarios)}</p>
            </div>
            """
        elif action == "clear_scenarios" and youtube_context:
            # Contextをクリア
            youtube_context.generated_scenarios.clear()
            youtube_context.is_scenarios_generated = False
            youtube_context.update_timestamp()

            return f"""
            <div style="background-color: #fff3e0; border: 1px solid #ff9800; border-radius: 4px; padding: 15px; margin: 10px 0;">
                <h4 style="color: #f57c00; margin: 0 0 15px 0;">🗑️ 企画案クリア</h4>
                <p style="font-size: 14px;">全ての企画案をクリアしました</p>
            </div>
            """

        return display_generic_tool_result(result, tool.name)

    def handle_cut_segment_operation(self, context, tool, result):
        """カットセグメント操作の処理"""
        youtube_context = getattr(context, "youtube_context", None) if context else None
        action = result.get("action", "")

        if action == "add_cut_segment" and youtube_context:
            segment_data = result.get("segment", {})
            # Contextに実際に追加
            youtube_context.cut_segments.append(segment_data)
            youtube_context.is_cuts_generated = True
            youtube_context.update_timestamp()

            return f"""
            <div style="background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 4px; padding: 15px; margin: 10px 0;">
                <h4 style="color: #2e7d32; margin: 0 0 15px 0;">✅ カットセグメント追加</h4>
                <p style="font-size: 14px;"><strong>時間:</strong> {segment_data.get('start_time', 0):.1f}s - {segment_data.get('end_time', 0):.1f}s</p>
            </div>
            """
        elif action == "clear_cut_segments" and youtube_context:
            # Contextをクリア
            youtube_context.is_cuts_generated = False
            youtube_context.update_timestamp()

            return f"""
            <div style="background-color: #fff3e0; border: 1px solid #ff9800; border-radius: 4px; padding: 15px; margin: 10px 0;">
                <h4 style="color: #f57c00; margin: 0 0 15px 0;">🗑️ カットセグメントクリア</h4>
                <p style="font-size: 14px;">全てのカットセグメントをクリアしました</p>
            </div>
            """

        return display_generic_tool_result(result, tool.name)
