# -*- coding: utf-8 -*-
"""YouTube動画生成ページ"""

import asyncio
import os
import traceback

from agents import Runner

import streamlit as st
from src.agent_sdk.context.youtube_scenario_context import YouTubeScenarioContext
from src.agent_sdk.hooks.youtube_agent_hooks import YouTubeAgentHooks
from src.agent_sdk.agents_registry.youtube_scenario import create_youtube_scenario_assistant
from src.agent_sdk.utils import create_model_selector, create_model_settings, create_reasoning_setting
from src.streamlit.components.login import check_login

check_login()
import pandas as pd

st.title("🎬 YouTube動画生成")

# サイドバーでの設定
st.sidebar.title("⚙️ 設定")

# モデル選択
model = create_model_selector()
reasoning_effort, reasoning_summary = create_reasoning_setting()

# YouTubeScenarioContextのインスタンス作成
if "youtube_context" not in st.session_state:
    st.session_state.youtube_context = YouTubeScenarioContext()

youtube_context = st.session_state.youtube_context

# YouTubeAgentHooksのインスタンス作成
hooks = YouTubeAgentHooks()

# エージェントの作成
agent = create_youtube_scenario_assistant(model=model, model_settings=create_model_settings(model, reasoning_effort, reasoning_summary), hooks=hooks)

# メイン画面のタブ構成
tab1, tab2, tab3, tab4 = st.tabs(["🎬 入力", "💡 企画編集", "⚙️ 動画生成", "📥 ダウンロード"])

with tab1:
    st.header("YouTube動画URL入力")

    # YouTube URL入力
    youtube_url = st.text_input(
        "YouTube動画のURLを入力してください",
        value="https://www.youtube.com/watch?v=V_WUPJD0K8A&ab_channel=%E5%AE%89%E9%87%8E%E3%81%9F%E3%81%8B%E3%81%B2%E3%82%8D%EF%BC%A0%E6%96%B0%E5%85%9A%E3%80%8C%E3%83%81%E3%83%BC%E3%83%A0%E3%81%BF%E3%82%89%E3%81%84%E3%80%8D%E5%85%AC%E5%BC%8F%E3%83%81%E3%83%A3%E3%83%B3%E3%83%8D%E3%83%AB",
        placeholder="https://www.youtube.com/watch?v=...",
        help="YouTube動画のURLを入力すると、動画情報を取得し、字幕を抽出します",
    )

    # 処理オプション
    col1, col2 = st.columns(2)
    with col1:
        download_video = st.checkbox("動画をダウンロード", value=True)
        extract_audio = st.checkbox("音声ファイルも抽出", value=False)

    with col2:
        video_quality = st.selectbox("動画品質", ["720p", "1080p", "480p"], index=0)
        process_transcript = st.checkbox("字幕を自動処理", value=True)

    # Cookies設定（エクスパンダーで隠す）
    with st.expander("🍪 YouTube Cookies設定 (ボット検出エラー対応)", expanded=False):
        st.warning("⚠️ ボット検出エラーが出た場合のみ設定してください")

        # Cookiesの説明
        st.markdown("**🚨 こんなエラーが出た時に使用:**")
        st.code("ERROR: [youtube] XXXXXXX: Sign in to confirm you're not a bot. Use --cookies-from-browser or --cookies", language="text")

        st.markdown("**📋 方法1: ブラウザ拡張機能（推奨）**")
        st.markdown("1. Chrome拡張機能「Get cookies.txt LOCALLY」をインストール")
        st.markdown("2. YouTubeにログインし、拡張機能をクリック")
        st.markdown("3. 出力されたテキストをそのまま貼り付け")

        st.markdown("**🔧 方法2: 手動取得**")
        st.markdown("1. Chromeで YouTube にログイン")
        st.markdown("2. F12 でデベロッパーツールを開く")
        st.markdown("3. Application → Storage → Cookies → https://www.youtube.com")
        st.markdown("4. 重要なCookies（HSID, SSID, APISID, SAPISID, SID等）をNetscape形式に変換")

        st.markdown("**🔒 セキュリティ注意事項:**")
        st.markdown("- Cookiesには個人情報が含まれます")
        st.markdown("- 他人と共有しないでください")
        st.markdown("- 使用後は定期的にYouTubeからログアウト・再ログインすることを推奨")

        youtube_cookies = st.text_area(
            "YouTube Cookies (Netscape形式)",
            value="",
            height=100,
            placeholder="# Netscape HTTP Cookie File\n# This is a generated file! Do not edit.\n\n.youtube.com\tTRUE\t/\tFALSE\t1234567890\tHSID\tAbc123...\n.youtube.com\tTRUE\t/\tFALSE\t1234567890\tSSID\tXyz789...",
            help="yt-dlpでボット検出エラーが出る場合にのみ必要です。空の場合は通常通り処理されます。",
        )

    # 解析・ダウンロードボタン
    if st.button("動画を解析・ダウンロード", type="primary", disabled=not youtube_url):
        if youtube_url:
            with st.spinner("動画をダウンロード中..."):
                try:
                    # YouTube URLをContextに設定
                    from src.lib.youtube.youtube_download import extract_video_id_from_url, get_video_info, download_youtube_video
                    from src.lib.youtube.transcript_extraction import extract_youtube_transcript

                    video_id = extract_video_id_from_url(youtube_url)

                    # 動画情報を取得
                    video_info_result = get_video_info(youtube_url, cookies=youtube_cookies if youtube_cookies.strip() else None)
                    if video_info_result.success:
                        video_info = video_info_result.metadata.dict()
                        youtube_context.set_video_info(video_info)
                        st.success(f"📹 動画情報を取得しました: {video_info['title']}")

                        # 動画情報をデバッグ表示
                        with st.expander("動画情報詳細"):
                            st.json(video_info)

                    # 動画をダウンロード（必要に応じて）
                    if download_video:
                        download_result = download_youtube_video(
                            youtube_url, video_quality=video_quality, include_audio=extract_audio, cookies=youtube_cookies if youtube_cookies.strip() else None
                        )
                        if download_result.success:
                            # Contextに動画パスを設定
                            youtube_context.set_video_paths(download_result.video_path, download_result.audio_path or "")
                            st.success(f"🎬 動画をダウンロードしました: {download_result.video_path}")
                        else:
                            st.warning(f"⚠️ 動画ダウンロードに失敗: {download_result.error}")
                    else:
                        st.info("💡 動画ダウンロードはスキップされました")

                    # 字幕を取得
                    transcript_result = extract_youtube_transcript(video_id)
                    if transcript_result["success"]:
                        # 字幕データを取得（transcript_resultの"transcript"キーから）
                        transcript_chunks = transcript_result["transcript"]

                        # 字幕を処理
                        if process_transcript:
                            # 文章分割と結合処理
                            from src.lib.youtube.transcript_extraction import split_transcript_by_sentence, merge_transcript_until_period, fix_transcript_text

                            split_chunks = split_transcript_by_sentence(transcript_chunks)
                            merged_chunks = merge_transcript_until_period(split_chunks)
                            processed_chunks = fix_transcript_text(merged_chunks)

                            youtube_context.set_processed_transcript(processed_chunks)
                            youtube_context.set_transcript_chunks(transcript_chunks)
                        else:
                            youtube_context.set_transcript_chunks(transcript_chunks)

                        st.success(f"📝 字幕を取得しました: {transcript_result['total_segments']}セグメント ({transcript_result['language']})")

                        # 字幕取得情報をデバッグ表示
                        with st.expander("字幕取得詳細"):
                            st.json(
                                {
                                    "language": transcript_result["language"],
                                    "total_segments": transcript_result["total_segments"],
                                    "available_languages": transcript_result["available_languages"],
                                }
                            )
                    else:
                        st.warning(f"⚠️ 字幕取得に失敗: {transcript_result.get('error', '不明なエラー')}")

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {str(e)}")
                    st.code(traceback.format_exc(), language="python")

    # 現在の状況表示
    status = youtube_context.get_processing_status()
    if youtube_context.video_url:
        st.success(f"📹 動画: {youtube_context.video_title or youtube_context.video_id}")

        # 動画情報表示
        if youtube_context.video_duration > 0:
            duration_minutes = int(youtube_context.video_duration // 60)
            duration_seconds = int(youtube_context.video_duration % 60)
            st.info(f"⏱️ 動画長: {duration_minutes}分{duration_seconds}秒 | チャンネル: {youtube_context.channel_name}")

        # ステータス表示
        status_cols = st.columns(4)
        status_items = [
            ("動画情報", bool(youtube_context.video_title)),
            ("字幕抽出", status["transcript_extracted"]),
            ("企画生成", status["scenarios_generated"]),
            ("カット生成", status["cuts_generated"]),
        ]

        for col, (label, completed) in zip(status_cols, status_items):
            with col:
                icon = "✅" if completed else "⏳"
                st.metric(label, icon)

        # 字幕データの表示
        if youtube_context.is_transcript_extracted:
            st.subheader("📝 取得された字幕")

            # 字幕データを表形式で表示
            import pandas as pd

            # 元のYouTubeチャンクを優先して表示
            transcript_data = youtube_context.transcript_chunks if youtube_context.transcript_chunks else youtube_context.processed_transcript
            if transcript_data:
                df_data = []
                for i, chunk in enumerate(transcript_data):  # 最初の50チャンクのみ表示
                    start_time = chunk.get("start", 0)
                    duration = chunk.get("duration", 0)
                    end_time = start_time + duration
                    df_data.append(
                        {
                            "開始時間": f"{int(start_time//60):02d}:{int(start_time%60):02d}",
                            "終了時間": f"{int(end_time//60):02d}:{int(end_time%60):02d}",
                            "テキスト": chunk.get("text", ""),
                        }
                    )

                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, height=300)

            # エージェント開始ボタン
            st.subheader("🤖 企画案生成の開始")
            if st.button("エージェントを開始してカット割りを生成", type="primary"):
                with st.spinner("エージェントが企画案を生成中..."):
                    try:
                        # エージェントに企画案生成を依頼
                        analysis_prompt = f"""
                        取得済みの字幕データに基づいて、YouTube Short用の企画案を生成してください。
                        
                        動画情報:
                        - タイトル: {youtube_context.video_title}
                        - 時間: {youtube_context.video_duration}秒
                        - チャンネル: {youtube_context.channel_name}
                        
                        5つの魅力的な企画案を作成し、それぞれに対して最適なカット割りを提案してください。
                        """

                        result = asyncio.run(Runner.run(starting_agent=agent, input=analysis_prompt, context=youtube_context, max_turns=50))

                        # エージェント実行結果からcontextの状態を更新
                        # resultオブジェクトを安全に表示（詳細はデバッグセクションで確認可能）
                        st.write("エージェント実行結果: 処理が完了しました")

                        # contextに生成されたシナリオがあるかチェック
                        if hasattr(result, "context"):
                            updated_context = result.context
                            # session_stateのcontextを更新
                            st.session_state.youtube_context = updated_context
                            youtube_context = updated_context

                        # デバッグ: contextの状態確認
                        context_status = {
                            "scenarios_generated": youtube_context.is_scenarios_generated,
                            "scenarios_count": len(youtube_context.generated_scenarios),
                            "cuts_generated": youtube_context.is_cuts_generated,
                        }
                        st.json(context_status)

                        st.success("✅ エージェントによる企画案生成が完了しました！")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ エージェント実行エラー: {str(e)}")
                        st.code(traceback.format_exc(), language="python")

with tab2:
    st.header("企画案編集・カット設定")

    if not youtube_context.is_transcript_extracted:
        st.info("まず「入力」タブで動画を解析してください。")
    else:
        # 企画案生成方法の選択
        generation_method = st.radio("企画案生成方法を選択:", ["🎛️ 設定から生成", "💬 チャットで生成"], horizontal=True)

        if generation_method == "🎛️ 設定から生成":
            # 従来の設定UI（コンパクト化）
            with st.expander("⚙️ 生成設定", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    num_scenarios = st.slider("企画案数", 1, 10, 3)
                with col2:
                    target_duration = st.slider("目標時間(秒)", 30, 180, 60)
                with col3:
                    scenario_style = st.selectbox("スタイル", ["汎用的", "エンタメ系", "教育系", "ビジネス系"])

                if st.button("📋 企画案を生成", type="primary"):
                    with st.spinner("企画案を生成中..."):
                        scenario_prompt = f"""
                        YouTube Short用の企画案を生成してください。生成する際には, cut_segments, subtitlesも生成してください。
                        
                        条件：
                        - 企画案数: {num_scenarios}個
                        - 目標時間: {target_duration}秒
                        - スタイル: {scenario_style}
                        
                        効果的で視聴者にアピールする企画案を作成してください。
                        """

                        try:
                            result = asyncio.run(Runner.run(starting_agent=agent, input=scenario_prompt, context=youtube_context, max_turns=50))

                            if hasattr(result, "context"):
                                updated_context = result.context
                                st.session_state.youtube_context = updated_context
                                youtube_context = updated_context

                            st.success("✅ 企画案が生成されました！")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ エラー: {str(e)}")

        else:  # チャット生成
            # チャットUI（コンパクト化）
            with st.expander("💬 エージェントチャット", expanded=True):
                # チャット履歴の初期化
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []

                # チャット履歴を表示（最新5件のみ）
                recent_messages = st.session_state.chat_history[-5:] if st.session_state.chat_history else []
                for message in recent_messages:
                    if message["role"] == "user":
                        with st.chat_message("user"):
                            st.write(message["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(message["content"])

                # チャット入力
                user_message = st.chat_input("例：バズりやすい企画を3つ作って、カットセグメントも生成して")

                if user_message:
                    # ユーザーメッセージをチャット履歴に追加
                    st.session_state.chat_history.append({"role": "user", "content": user_message})

                    with st.spinner("エージェントが処理中..."):
                        try:
                            result = asyncio.run(Runner.run(starting_agent=agent, input=user_message, context=youtube_context, max_turns=50))

                            if hasattr(result, "context"):
                                updated_context = result.context
                                st.session_state.youtube_context = updated_context
                                youtube_context = updated_context

                            agent_response = "処理が完了しました。下の企画案一覧をご確認ください。"
                            st.session_state.chat_history.append({"role": "assistant", "content": agent_response})

                            st.rerun()

                        except Exception as e:
                            error_message = f"エラー: {str(e)}"
                            st.session_state.chat_history.append({"role": "assistant", "content": error_message})
                            st.error(error_message)

                # チャット履歴管理
                if len(st.session_state.chat_history) > 0:
                    if st.button("🗑️ チャット履歴をクリア", key="clear_chat"):
                        st.session_state.chat_history = []
                        st.rerun()

        st.divider()

        # 企画案表示エリア
        st.subheader("📋 生成された企画案")

        # 生成された企画案の表示と選択
        if youtube_context.generated_scenarios:
            # 企画案の総数を表示
            st.info(f"💡 生成済み企画案: {len(youtube_context.generated_scenarios)}件")

            selected_scenarios = []
            for i, scenario in enumerate(youtube_context.generated_scenarios):
                with st.expander(f"企画案 {i+1}: {scenario.get('title', 'タイトルなし')}", expanded=i < 3):
                    # 企画案の詳細を整理して表示
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**🎯 最初のインパクト**")
                        st.write(scenario.get("first_impact", "N/A"))

                        st.markdown("**🎪 ターゲット視聴者**")
                        st.write(scenario.get("target_audience", "N/A"))

                    with col2:
                        st.markdown("**🎭 結論・オチ**")
                        st.write(scenario.get("last_conclusion", "N/A"))

                        st.markdown("**📈 予想エンゲージメント**")
                        st.write(scenario.get("estimated_engagement", "N/A"))

                    st.markdown("**📝 企画概要**")
                    st.write(scenario.get("summary", "N/A"))

                    st.markdown("**🎣 フック戦略**")
                    st.write(scenario.get("hook_strategy", "N/A"))

                    # カットセグメント表示・編集
                    cut_segments = scenario.get("cut_segments", [])
                    subtitles = scenario.get("subtitles", [])

                    st.markdown("**✂️ カットセグメント編集**")

                    # 字幕情報の表示
                    if subtitles:
                        st.write(f"📝 整形済み字幕: {len(subtitles)}項目")
                        # expander内なので詳細表示にはcontainerを使用
                        with st.container():
                            st.markdown("**字幕一覧（最初の10項目）**")
                            for j, subtitle in enumerate(subtitles[:10]):  # 最初の10項目のみ表示
                                # 改行コードを適切に表示
                                subtitle_text = subtitle.get("text", "").replace("\\n", "\n")
                                st.text(f"{j+1}. {subtitle.get('start_time', 0):.1f}s-{subtitle.get('end_time', 0):.1f}s:")
                                st.text(f"   {subtitle_text}")
                            if len(subtitles) > 10:
                                st.text(f"...他{len(subtitles) - 10}項目")

                    if cut_segments:
                        st.write(f"📊 現在のセグメント数: {len(cut_segments)}個")
                        total_duration = sum(seg.get("end_time", 0) - seg.get("start_time", 0) for seg in cut_segments)
                        st.write(f"📈 合計時間: {total_duration:.1f}秒")

                        # カットセグメント一覧と編集
                        for j, segment in enumerate(cut_segments):
                            with st.container():
                                st.markdown(f"**セグメント {j+1}**")
                                seg_col1, seg_col2, seg_col3 = st.columns([2, 2, 3])

                                with seg_col1:
                                    start_time = st.number_input("開始時間(秒)", value=float(segment.get("start_time", 0)), key=f"start_time_{i}_{j}", format="%.1f", min_value=0.0)

                                with seg_col2:
                                    end_time = st.number_input(
                                        "終了時間(秒)", value=float(segment.get("end_time", 0)), key=f"end_time_{i}_{j}", format="%.1f", min_value=start_time + 0.1
                                    )

                                with seg_col3:
                                    duration = end_time - start_time
                                    st.metric("長さ", f"{duration:.1f}秒")

                                content = st.text_area("内容・説明", value=segment.get("content", ""), key=f"content_{i}_{j}", height=68)

                                purpose = st.text_input("目的", value=segment.get("purpose", ""), key=f"purpose_{i}_{j}")

                                # セグメント削除ボタン
                                if st.button(f"🗑️ セグメント {j+1} を削除", key=f"delete_segment_{i}_{j}"):
                                    scenario["cut_segments"].pop(j)
                                    st.rerun()

                                st.divider()
                    else:
                        st.info("まだカットセグメントが生成されていません。")

                    # カットセグメント生成・追加ボタン
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button(f"🎬 カットセグメントを生成", key=f"generate_cuts_{i}"):
                            with st.spinner("カットセグメントを生成中..."):
                                cuts_prompt = f"""
                                    企画案「{scenario.get('title')}」に基づいてカットセグメントを生成してください。
                                    
                                    企画詳細:
                                    - インパクト: {scenario.get('first_impact')}
                                    - 結論: {scenario.get('last_conclusion')}
                                    - 概要: {scenario.get('summary')}
                                    
                                    効果的で視聴者を惹きつけるカットセグメントを作成してください。
                                    """

                                try:
                                    result = asyncio.run(Runner.run(starting_agent=agent, input=cuts_prompt, context=youtube_context, max_turns=50))

                                    if hasattr(result, "context"):
                                        updated_context = result.context
                                        st.session_state.youtube_context = updated_context
                                        youtube_context = updated_context

                                    st.success("✅ カットセグメントが生成されました！")
                                    st.rerun()

                                except Exception as e:
                                    st.error(f"❌ エラー: {str(e)}")

                    with col_btn2:
                        if st.button(f"➕ 手動セグメント追加", key=f"add_segment_{i}"):
                            new_segment = {"start_time": 0.0, "end_time": 10.0, "content": "新しいセグメント", "purpose": "", "editing_notes": ""}
                            scenario.setdefault("cut_segments", []).append(new_segment)
                            st.rerun()

                    # 選択チェックボックス
                    if st.checkbox(f"📌 この企画案を選択", key=f"scenario_select_{i}"):
                        selected_scenarios.append(i)

            # 選択結果を保存
            if selected_scenarios:
                st.success(f"✅ {len(selected_scenarios)}件の企画案が選択されています")

            if st.button("🚀 選択した企画案でカット割りを生成", disabled=not selected_scenarios, type="primary"):
                youtube_context.select_scenarios(selected_scenarios)
                st.success(f"✅ {len(selected_scenarios)}個の企画案を選択しました！")
                st.rerun()
        else:
            st.info("💡 まだ企画案がありません。左側のチャットでエージェントに企画案生成を依頼してください。")
            st.markdown("**チャット例:**")
            st.code("企画案を5個生成して")
            st.code("バズりやすい企画を3つ作って")
            st.code("エンタメ系の企画案をお願いします")

with tab3:
    st.header("動画生成")

    if not youtube_context.generated_scenarios:
        st.info("まず「企画編集」タブで企画案を生成してください。")
    else:
        st.subheader("🎬 企画案選択・動画生成")

        # 企画案の選択
        scenarios_with_cuts = []
        for i, scenario in enumerate(youtube_context.generated_scenarios):
            cut_segments = scenario.get("cut_segments", [])
            if cut_segments:  # カットセグメントがある企画案のみ表示
                scenarios_with_cuts.append((i, scenario))

        if not scenarios_with_cuts:
            st.warning("⚠️ カットセグメントが設定された企画案がありません。「企画編集」タブでカットセグメントを生成してください。")
        else:
            st.info(f"📝 動画生成可能な企画案: {len(scenarios_with_cuts)}件")

            # 企画案選択
            scenario_options = [f"{scenario['title']} ({len(scenario.get('cut_segments', []))}セグメント)" for _, scenario in scenarios_with_cuts]

            selected_scenario_idx = st.selectbox(
                "動画にする企画案を選択",
                range(len(scenarios_with_cuts)),
                format_func=lambda x: scenario_options[x],
                help="カットセグメントが設定されている企画案から選択してください",
            )

            if selected_scenario_idx is not None:
                original_idx, selected_scenario = scenarios_with_cuts[selected_scenario_idx]

                # 選択された企画案の詳細表示
                with st.expander(f"📋 選択中: {selected_scenario['title']}", expanded=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**🎯 最初のインパクト**")
                        st.write(selected_scenario.get("first_impact", "N/A"))

                        st.markdown("**🎭 結論・オチ**")
                        st.write(selected_scenario.get("last_conclusion", "N/A"))

                    with col2:
                        st.markdown("**📝 企画概要**")
                        st.write(selected_scenario.get("summary", "N/A"))

                        # カットセグメント情報
                        cut_segments = selected_scenario.get("cut_segments", [])
                        total_duration = sum(seg.get("end_time", 0) - seg.get("start_time", 0) for seg in cut_segments)
                        st.metric("総再生時間", f"{total_duration:.1f}秒")
                        st.metric("セグメント数", f"{len(cut_segments)}個")

                # 動画生成設定
                st.subheader("⚙️ 動画生成設定")

                col1, col2 = st.columns(2)
                with col1:
                    output_format = st.selectbox("出力フォーマット", ["mp4", "mov"], index=0)
                    video_quality = st.selectbox("動画品質", ["high", "medium", "low"], index=0)
                    add_subtitles = st.checkbox("字幕を追加", value=True)

                with col2:
                    add_bgm = st.checkbox("BGMを追加", value=False)
                    if add_bgm:
                        bgm_file = st.file_uploader("BGMファイル", type=["mp3", "wav", "m4a"])

                # 動画生成ボタン
                if st.button("🎬 動画を生成", type="primary", disabled=not cut_segments):
                    with st.spinner("動画を生成中...この処理には時間がかかる場合があります..."):
                        try:
                            # video_processing.pyから直接ffmpegを実行
                            from src.lib.youtube.video_processing import create_short_video, create_subtitle_file
                            import tempfile

                            # プログレスバーの設定
                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            def progress_callback(message, progress):
                                status_text.text(message)
                                progress_bar.progress(progress)

                            # 動画ファイルのパスを取得（YouTube動画をダウンロード済みと仮定）
                            source_video_path = youtube_context.downloaded_video_path if hasattr(youtube_context, "downloaded_video_path") else None

                            if not source_video_path:
                                st.error("❌ 動画ファイルが見つかりません。まず動画をダウンロードしてください。")
                                st.stop()

                            # 出力ディレクトリの作成
                            output_dir = tempfile.mkdtemp()
                            output_path = os.path.join(output_dir, f"youtube_short_{selected_scenario['title'].replace(' ', '_')}.{output_format}")

                            # 選択された企画案のカットセグメントを使用
                            scenario_cut_segments = cut_segments

                            # 字幕ファイルの作成（必要に応じて）
                            subtitle_path = None
                            if add_subtitles and youtube_context.transcript_chunks:
                                # エージェントが整形したsubtitlesを優先使用
                                scenario_subtitles = selected_scenario.get("subtitles", [])
                                # ASS形式で字幕を作成（フォントサイズを確実に制御）
                                subtitle_result = create_subtitle_file(
                                    youtube_context.transcript_chunks, scenario_cut_segments, format="ass", scenario_subtitles=scenario_subtitles
                                )
                                if subtitle_result["success"]:
                                    subtitle_path = subtitle_result["subtitle_path"]

                            # BGMファイルのパス（必要に応じて）
                            bgm_path = None
                            if add_bgm and bgm_file:
                                # BGMファイルを一時保存
                                bgm_temp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{bgm_file.name.split('.')[-1]}")
                                bgm_temp.write(bgm_file.read())
                                bgm_path = bgm_temp.name
                                bgm_temp.close()

                            # 動画生成実行
                            result = create_short_video(
                                source_video_path=source_video_path,
                                cut_segments=scenario_cut_segments,
                                output_path=output_path,
                                subtitle_path=subtitle_path,
                                bgm_path=bgm_path,
                                video_format=output_format,
                                quality=video_quality,
                                progress_callback=progress_callback,
                                scenario_info=selected_scenario,  # 企画情報を渡す
                            )

                            if result.success:
                                # 結果をcontextに保存
                                youtube_context.set_output_path(result.output_path)

                                st.success("✅ 動画が生成されました！")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ 動画生成に失敗しました: {result.error}")

                        except Exception as e:
                            st.error(f"❌ エラーが発生しました: {str(e)}")
                            st.code(traceback.format_exc(), language="python")

with tab4:
    st.header("ダウンロード")

    if not youtube_context.is_video_processed:
        st.info("まず「動画生成」タブで動画を生成してください。")
    else:
        st.success("🎉 動画生成が完了しました！")

        # 2カラムレイアウト
        col_left, col_right = st.columns([1, 2])

        with col_left:
            st.subheader("📹 生成された動画")

            # 生成された動画の情報表示
            if youtube_context.output_video_path and os.path.exists(youtube_context.output_video_path):
                # 動画プレビュー
                st.video(youtube_context.output_video_path)

                # ファイル情報
                file_size = os.path.getsize(youtube_context.output_video_path) / (1024 * 1024)
                st.write(f"**ファイルサイズ:** {file_size:.1f} MB")

                # 動画の詳細情報
                if youtube_context.video_title:
                    st.write(f"**タイトル:** {youtube_context.video_title}")
                if youtube_context.channel_name:
                    st.write(f"**チャンネル:** {youtube_context.channel_name}")
            else:
                st.warning("動画ファイルが見つかりません。")

        with col_right:
            st.subheader("📥 ダウンロード")

            # メイン動画ダウンロード
            if youtube_context.output_video_path and os.path.exists(youtube_context.output_video_path):
                with open(youtube_context.output_video_path, "rb") as file:
                    st.download_button(
                        label="🎬 動画をダウンロード",
                        data=file.read(),
                        file_name=f"youtube_short_{youtube_context.video_id}.mp4",
                        mime="video/mp4",
                        type="primary",
                        use_container_width=True,
                    )

            st.divider()

            # 字幕データ
            if youtube_context.transcript_chunks:
                import json

                transcript_json = json.dumps(youtube_context.transcript_chunks, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📝 字幕データ (元)",
                    data=transcript_json,
                    file_name=f"transcript_original_{youtube_context.video_id}.json",
                    mime="application/json",
                    use_container_width=True,
                )

            # 処理済み字幕データ
            if youtube_context.processed_transcript:
                import json

                processed_json = json.dumps(youtube_context.processed_transcript, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📝 字幕データ (処理済み)",
                    data=processed_json,
                    file_name=f"transcript_processed_{youtube_context.video_id}.json",
                    mime="application/json",
                    use_container_width=True,
                )

            # 企画案データ
            if youtube_context.generated_scenarios:
                import json

                scenarios_json = json.dumps(youtube_context.generated_scenarios, ensure_ascii=False, indent=2)
                st.download_button(
                    label="💡 企画案データ", data=scenarios_json, file_name=f"scenarios_{youtube_context.video_id}.json", mime="application/json", use_container_width=True
                )

            # 動画情報データ
            if youtube_context.video_id:
                import json

                video_info_data = {
                    "video_id": youtube_context.video_id,
                    "video_url": youtube_context.video_url,
                    "title": youtube_context.video_title,
                    "channel": youtube_context.channel_name,
                    "duration": youtube_context.video_duration,
                    "view_count": youtube_context.view_count,
                    "like_count": youtube_context.like_count,
                    "upload_date": youtube_context.upload_date,
                    "processing_summary": youtube_context.get_processing_summary(),
                }
                video_info_json = json.dumps(video_info_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📋 動画情報", data=video_info_json, file_name=f"video_info_{youtube_context.video_id}.json", mime="application/json", use_container_width=True
                )

            st.divider()

            # ダウンロード統計
            download_stats = []
            if youtube_context.output_video_path and os.path.exists(youtube_context.output_video_path):
                download_stats.append("🎬 動画")
            if youtube_context.transcript_chunks:
                download_stats.append("📝 字幕")
            if youtube_context.generated_scenarios:
                download_stats.append("💡 企画案")

            if download_stats:
                st.success(f"利用可能: {', '.join(download_stats)}")
            else:
                st.info("ダウンロード可能なファイルがありません")

# サイドバーにContext情報を表示
with st.sidebar:
    st.subheader("📊 処理状況")
    context_info = youtube_context.to_dict()

    if context_info["video_url"]:
        st.write(f"**動画ID:** {context_info['video_id']}")
        st.write(f"**タイトル:** {context_info['video_title'][:30]}..." if context_info["video_title"] else "")
        st.write(f"**字幕セグメント:** {context_info['transcript_chunks_count']}")
        st.write(f"**企画案数:** {context_info['generated_scenarios_count']}")
        st.write(f"**カットセグメント:** {context_info.get('total_cut_segments_count', 0)}")
        if context_info.get("scenario_cut_segments_count", 0) > 0:
            st.write(f"　└ シナリオ内: {context_info['scenario_cut_segments_count']}")

    # リセットボタン
    if st.button("🔄 すべてリセット"):
        st.session_state.youtube_context = YouTubeScenarioContext()
        st.rerun()
