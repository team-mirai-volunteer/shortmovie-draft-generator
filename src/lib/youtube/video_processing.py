# -*- coding: utf-8 -*-
"""動画処理・編集用ツール"""

import os
import tempfile
from typing import Dict, List, Any, Optional
import ffmpeg
from src.agent_sdk.schemas.youtube import VideoProcessingResult


def get_system_font_path() -> str:
    """システムフォントパスを取得"""
    import platform

    system = platform.system()

    if system == "Darwin":  # macOS
        return "/System/Library/Fonts/Helvetica.ttc"
    elif system == "Windows":
        return "C:/Windows/Fonts/arial.ttf"
    elif system == "Linux":
        # よく使われるフォントパスを試す
        font_paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/TTF/arial.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        return ""  # フォントが見つからない場合は空文字列
    else:
        return ""


def create_short_video(
    source_video_path: str,
    cut_segments: List[Dict[str, Any]],  # 一時的に古い型を保持
    output_path: Optional[str] = None,
    subtitle_path: Optional[str] = None,
    bgm_path: Optional[str] = None,
    video_format: str = "mp4",
    quality: str = "high",
    progress_callback: Optional[callable] = None,
    scenario_info: Optional[Dict[str, Any]] = None,  # 企画情報を追加
) -> VideoProcessingResult:
    """カットセグメントに基づいてショート動画を作成する

    Args:
        source_video_path: 元動画ファイルのパス
        cut_segments: カットセグメントのリスト
        output_path: 出力ファイルパス
        subtitle_path: 字幕ファイルパス
        bgm_path: BGMファイルパス
        video_format: 出力フォーマット
        quality: 動画品質
        progress_callback: 進捗コールバック関数

    Returns:
        処理結果を含む辞書
    """
    try:
        # 出力パス設定
        if output_path is None:
            output_dir = tempfile.mkdtemp()
            output_path = os.path.join(output_dir, f"short_video.{video_format}")

        # セグメント検証
        if not cut_segments:
            return VideoProcessingResult(success=False, error="カットセグメントが指定されていません")

        # 元動画の音声トラック確認（最初に一度だけ実行）
        try:
            probe_result = ffmpeg.probe(source_video_path)
            has_audio = any(stream["codec_type"] == "audio" for stream in probe_result["streams"])
            print(f"DEBUG: 元動画に音声トラック: {has_audio}")
        except Exception as e:
            print(f"DEBUG: 音声トラック確認エラー: {e}")
            has_audio = True  # エラーの場合は音声ありと仮定

        # 一時ディレクトリ作成
        temp_dir = tempfile.mkdtemp()
        segment_files = []

        # 各セグメントを切り出し
        print(f"DEBUG: 処理するセグメント数: {len(cut_segments)}")
        for i, segment in enumerate(cut_segments):
            if progress_callback:
                progress_callback(f"セグメント {i+1}/{len(cut_segments)} を処理中...", (i / len(cut_segments)) * 0.7)

            start_time = segment.get("start_time", 0)
            end_time = segment.get("end_time", 0)
            print(f"DEBUG: セグメント {i+1}: {start_time}s - {end_time}s")

            if end_time <= start_time:
                print(f"DEBUG: セグメント {i+1} スキップ: 無効な時間範囲 ({start_time} >= {end_time})")
                continue

            segment_path = os.path.join(temp_dir, f"segment_{i:03d}.mp4")

            try:
                # 企画情報を取得
                segment_title = segment.get("content", "")
                segment_purpose = segment.get("purpose", "")

                # 企画案全体の情報も取得
                scenario_title = ""
                scenario_hook = ""
                if scenario_info:
                    scenario_title = scenario_info.get("title", "")
                    scenario_hook = scenario_info.get("first_impact", "")

                # ffmpegで切り出し（縦動画レイアウト）
                input_stream = ffmpeg.input(source_video_path, ss=start_time, to=end_time)

                # 元動画のアスペクト比を保持してリサイズ（縦動画内に収まるように）
                video_stream = input_stream.video.filter("scale", w=1080, h=1080, force_original_aspect_ratio="decrease")

                # 縦動画キャンバス（1080x1920）を作成し、中央に元動画を配置
                video_stream = video_stream.filter("pad", w=1080, h=1920, x="(ow-iw)/2", y="(oh-ih)/2", color="black")

                # システムフォントパスを取得
                font_path = get_system_font_path()

                # テキストオーバーレイは一時的に無効化してテスト
                print(f"DEBUG: テキストオーバーレイは一時的に無効化中")

                if has_audio:
                    audio_stream = input_stream.audio
                    cmd = ffmpeg.output(video_stream, audio_stream, segment_path, vcodec="libx264", acodec="aac", preset="fast", crf=23).overwrite_output()
                else:
                    cmd = ffmpeg.output(video_stream, segment_path, vcodec="libx264", preset="fast", crf=23).overwrite_output()

                print(f"DEBUG: FFmpeg コマンド実行中...")
                try:
                    cmd.run(quiet=False, capture_stdout=True, capture_stderr=True)
                    print(f"DEBUG: セグメント {i+1} 処理完了: {segment_path}")
                    # ファイルが実際に作成されたかチェック
                    if os.path.exists(segment_path):
                        file_size = os.path.getsize(segment_path)
                        print(f"DEBUG: 作成されたファイルサイズ: {file_size} bytes")
                    else:
                        print(f"DEBUG: ファイルが作成されませんでした: {segment_path}")
                except ffmpeg.Error as e:
                    print(f"DEBUG: FFmpeg エラー - stdout: {e.stdout}")
                    print(f"DEBUG: FFmpeg エラー - stderr: {e.stderr}")
                    continue

            except Exception as e:
                print(f"DEBUG: セグメント {i+1} 処理エラー: {e}")
                import traceback

                print(f"DEBUG: スタックトレース: {traceback.format_exc()}")
                continue

            if os.path.exists(segment_path):
                segment_files.append(segment_path)

        print(f"DEBUG: 最終的に作成されたセグメントファイル数: {len(segment_files)}")
        if segment_files:
            for i, file_path in enumerate(segment_files):
                print(f"DEBUG: セグメントファイル {i+1}: {file_path}")

        if not segment_files:
            error_msg = f"有効なセグメントが見つかりませんでした。処理されたセグメント数: {len(cut_segments)}"
            print(f"DEBUG: {error_msg}")
            return VideoProcessingResult(success=False, error=error_msg)

        # セグメント結合用のファイルリスト作成
        concat_file_path = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_file_path, "w", encoding="utf-8") as f:
            for segment_file in segment_files:
                f.write(f"file '{segment_file}'\n")

        # セグメント結合
        if progress_callback:
            progress_callback("セグメントを結合中...", 0.7)

        temp_output = os.path.join(temp_dir, f"merged.{video_format}")
        try:
            (
                ffmpeg.input(concat_file_path, format="concat", safe=0)
                .output(temp_output, vcodec="copy", acodec="copy")  # 映像と音声を明示的にコピー
                .overwrite_output()
                .run(quiet=True)
            )

            # 結合後の音声確認
            try:
                merge_probe = ffmpeg.probe(temp_output)
                merged_has_audio = any(stream["codec_type"] == "audio" for stream in merge_probe["streams"])
                print(f"DEBUG: 結合後動画に音声トラック: {merged_has_audio}")
            except Exception as e:
                print(f"DEBUG: 結合後音声確認エラー: {e}")

        except Exception as e:
            print(f"DEBUG: セグメント結合エラー: {e}")
            return VideoProcessingResult(success=False, error=f"セグメント結合エラー: {str(e)}")

        # 字幕追加（必要に応じて）
        if subtitle_path and os.path.exists(subtitle_path):
            if progress_callback:
                progress_callback("字幕を追加中...", 0.8)
            temp_with_subs = os.path.join(temp_dir, f"with_subs.{video_format}")
            # パスのエスケープ処理を事前に行う
            escaped_subtitle_path = subtitle_path.replace(":", "\\:")

            # ファイル拡張子で字幕処理を切り替え
            if subtitle_path.lower().endswith(".ass"):
                # ASS形式の場合：フォントサイズは埋め込み済み、force_styleは不要
                subtitle_filter = f"subtitles={escaped_subtitle_path}"
            else:
                # SRT/VTT形式の場合：force_styleでスタイリング
                subtitle_filter = f"subtitles={escaped_subtitle_path}:force_style='Fontsize=48,Bold=1,OutlineColour=&H00000000,Outline=3,Shadow=2,MarginV=120,Alignment=2'"

            (ffmpeg.input(temp_output).output(temp_with_subs, vf=subtitle_filter, vcodec="libx264", acodec="copy", preset="fast", crf=23).overwrite_output().run(quiet=True))
            temp_output = temp_with_subs

        # BGM追加（必要に応じて）
        if bgm_path and os.path.exists(bgm_path):
            if progress_callback:
                progress_callback("BGMを追加中...", 0.9)
            temp_with_bgm = os.path.join(temp_dir, f"with_bgm.{video_format}")
            (
                ffmpeg.input(temp_output)
                .input(bgm_path)
                .filter_complex("[1:a]volume=0.2[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]")
                .output(temp_with_bgm, **{"map": ["0:v", "[aout]"]}, vcodec="copy", acodec="aac")
                .overwrite_output()
                .run(quiet=True)
            )
            temp_output = temp_with_bgm

        # 最終出力
        if progress_callback:
            progress_callback("最終出力を生成中...", 0.95)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if temp_output != output_path:
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_output, output_path)

        # 一時ファイル削除
        cleanup_temp_directory(temp_dir)

        # 結果情報取得
        video_info = get_video_info(output_path)

        if progress_callback:
            progress_callback("完了!", 1.0)

        return VideoProcessingResult(
            success=True,
            output_path=output_path,
            video_info=video_info,
            segments_processed=len(segment_files),
            processing_details={"subtitle_added": subtitle_path is not None, "bgm_added": bgm_path is not None, "format": video_format, "quality": quality},
        )

    except Exception as e:
        return VideoProcessingResult(success=False, error=f"動画処理エラー: {str(e)}")


def create_subtitle_file(
    transcript_chunks: List[Dict[str, Any]],
    cut_segments: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    format: str = "srt",
    scenario_subtitles: Optional[List[Dict[str, Any]]] = None,
    use_corrected_text: bool = True,
) -> Dict[str, Any]:
    """カットセグメントに対応する字幕ファイルを作成する

    Args:
        transcript_chunks: YouTubeから取得した字幕チャンク（結合処理なし）
        cut_segments: カットセグメント
        output_path: 出力ファイルパス
        format: 字幕ファイル形式（srt, vtt, ass）
        scenario_subtitles: エージェントが整形した字幕データ（優先使用）
        use_corrected_text: テキスト補正を使用するかどうか

    Returns:
        処理結果を含む辞書
    """
    try:
        if output_path is None:
            output_dir = tempfile.mkdtemp()
            output_path = os.path.join(output_dir, f"subtitles.{format}")

        # 字幕データの処理：生の字幕chunkベースで補正テキストを適用
        segment_subtitles = []

        print(f"DEBUG: 生字幕ベース字幕作成 - transcript_chunks数: {len(transcript_chunks)}")
        print(f"DEBUG: cut_segments数: {len(cut_segments)}")

        # 補正テキストマッピングを作成（scenario_subtitlesがある場合）
        correction_mapping = {}
        if scenario_subtitles and use_corrected_text:
            print(f"DEBUG: 補正テキストマッピングを作成 - {len(scenario_subtitles)}項目")
            for subtitle in scenario_subtitles:
                original_start = subtitle.get("start_time", 0)
                original_end = subtitle.get("end_time", 0)
                corrected_text = subtitle.get("text", "")
                # 時間範囲をキーとして補正テキストを保存
                correction_mapping[f"{original_start:.1f}-{original_end:.1f}"] = corrected_text

        # YouTubeの生字幕chunkから抽出（従来の処理）
        current_time_offset = 0
        for i, segment in enumerate(cut_segments):
            start_time = segment.get("start_time", 0)
            end_time = segment.get("end_time", 0)

            print(f"DEBUG: セグメント{i+1}: {start_time}s - {end_time}s")

            # このセグメントに含まれる字幕チャンクを探す
            segment_chunks = []
            for chunk in transcript_chunks:
                chunk_start = chunk.get("start", 0)
                chunk_duration = chunk.get("duration", 0)
                chunk_end = chunk_start + chunk_duration

                # セグメント範囲と重複する字幕チャンクを抽出（部分重複も含む）
                if chunk_start < end_time and chunk_end > start_time:
                    # セグメント境界での切り取り
                    effective_start = max(chunk_start, start_time)
                    effective_end = min(chunk_end, end_time)

                    # 新しい時間軸に調整（セグメント開始を0とする）
                    adjusted_start = current_time_offset + (effective_start - start_time)
                    adjusted_end = current_time_offset + (effective_end - start_time)

                    # 有効な時間範囲のもののみ追加（最小0.1秒の長さを保証）
                    if adjusted_end > adjusted_start and (adjusted_end - adjusted_start) >= 0.1:
                        original_text = chunk.get("text", "").strip()

                        # 補正テキストがあるかチェック
                        corrected_text = original_text
                        if correction_mapping:
                            # 元の時間範囲で補正テキストを検索
                            correction_key = f"{chunk_start:.1f}-{chunk_end:.1f}"
                            if correction_key in correction_mapping:
                                corrected_text = correction_mapping[correction_key]
                                print(f"DEBUG: テキスト補正適用 - {original_text[:20]}... → {corrected_text[:20]}...")

                        if corrected_text:  # 空でないテキストのみ
                            segment_chunks.append({"start": adjusted_start, "end": adjusted_end, "text": corrected_text})
                            print(f"DEBUG: 字幕chunk追加 - {adjusted_start:.1f}s-{adjusted_end:.1f}s: {corrected_text[:20]}...")

            print(f"DEBUG: セグメント{i+1}に含まれる字幕chunk数: {len(segment_chunks)}")
            segment_subtitles.extend(segment_chunks)

            # 次のセグメントのためのオフセット更新
            current_time_offset += end_time - start_time

        print(f"DEBUG: 最終的な字幕数: {len(segment_subtitles)}")

        # 字幕ファイル作成
        if format.lower() == "srt":
            content = create_srt_content(segment_subtitles)
        elif format.lower() == "vtt":
            content = create_vtt_content(segment_subtitles)
        elif format.lower() == "ass":
            content = create_ass_content(segment_subtitles)
        else:
            return {"success": False, "error": f"サポートされていない字幕形式: {format}", "subtitle_path": None}

        # ファイル保存
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"DEBUG: 字幕ファイル作成完了: {output_path}")
        return {"success": True, "error": None, "subtitle_path": output_path, "format": format, "subtitle_count": len(segment_subtitles)}

    except Exception as e:
        print(f"DEBUG: 字幕ファイル作成エラー: {e}")
        return {"success": False, "error": f"字幕ファイル作成エラー: {str(e)}", "subtitle_path": None}


def create_srt_content(subtitles: List[Dict[str, Any]]) -> str:
    """SRT形式の字幕コンテンツを作成"""
    content = ""
    subtitle_index = 1

    for subtitle in subtitles:
        start_time_seconds = subtitle["start"]
        end_time_seconds = subtitle["end"]
        text = subtitle["text"].strip()

        # 有効な字幕のみ追加（空テキストや無効な時間範囲を除外）
        if text and end_time_seconds > start_time_seconds and start_time_seconds >= 0:
            start_time = format_srt_time(start_time_seconds)
            end_time = format_srt_time(end_time_seconds)

            content += f"{subtitle_index}\n"
            content += f"{start_time} --> {end_time}\n"
            content += f"{text}\n\n"
            subtitle_index += 1

            print(f"DEBUG: SRT追加 - {subtitle_index-1}: {start_time} --> {end_time} | {text[:30]}...")

    print(f"DEBUG: SRT作成完了 - 総字幕数: {subtitle_index-1}")
    return content


def create_vtt_content(subtitles: List[Dict[str, Any]]) -> str:
    """WebVTT形式の字幕コンテンツを作成"""
    content = "WEBVTT\n\n"

    for subtitle in subtitles:
        start_time = format_vtt_time(subtitle["start"])
        end_time = format_vtt_time(subtitle["end"])
        text = subtitle["text"].strip()

        if text:
            content += f"{start_time} --> {end_time}\n"
            content += f"{text}\n\n"

    return content


def create_ass_content(subtitles: List[Dict[str, Any]]) -> str:
    """ASS形式の字幕コンテンツを作成（フォントサイズ埋め込み）"""
    # ASSファイルのヘッダー（縦動画用に最適化）
    content = """[Script Info]
Title: YouTube Short Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,2,2,50,50,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

"""

    for subtitle in subtitles:
        start_time_seconds = subtitle["start"]
        end_time_seconds = subtitle["end"]
        text = subtitle["text"].strip()

        if text and end_time_seconds > start_time_seconds and start_time_seconds >= 0:
            start_time = format_ass_time(start_time_seconds)
            end_time = format_ass_time(end_time_seconds)

            # ASSでは特殊文字をエスケープ
            text = text.replace("\n", "\\N")

            content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"

    return content


def format_srt_time(seconds: float) -> str:
    """秒数をSRT時間形式に変換"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"


def format_vtt_time(seconds: float) -> str:
    """秒数をWebVTT時間形式に変換"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"


def format_ass_time(seconds: float) -> str:
    """秒数をASS時間形式に変換 (H:MM:SS.CC)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int((seconds % 1) * 100)

    return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"


def get_video_info(video_path: str) -> Dict[str, Any]:
    """動画ファイルの情報を取得"""
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
        audio_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "audio"), None)

        info = {
            "duration": float(probe["format"].get("duration", 0)),
            "size": int(probe["format"].get("size", 0)),
            "bitrate": int(probe["format"].get("bit_rate", 0)),
        }

        if video_stream:
            info.update(
                {
                    "width": int(video_stream.get("width", 0)),
                    "height": int(video_stream.get("height", 0)),
                    "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                    "video_codec": video_stream.get("codec_name", ""),
                }
            )

        if audio_stream:
            info.update(
                {
                    "audio_codec": audio_stream.get("codec_name", ""),
                    "sample_rate": int(audio_stream.get("sample_rate", 0)),
                    "channels": int(audio_stream.get("channels", 0)),
                }
            )

        return info

    except Exception as e:
        return {"error": str(e)}


def cleanup_temp_directory(temp_dir: str) -> bool:
    """一時ディレクトリを削除"""
    try:
        import shutil

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"一時ディレクトリ削除エラー: {e}")
        return False


def estimate_processing_time(video_duration: float, num_segments: int, has_subtitles: bool = False, has_bgm: bool = False) -> float:
    """動画処理時間を推定"""
    base_time = video_duration * 0.1  # 基本処理時間
    segment_overhead = num_segments * 2  # セグメント数による追加時間
    subtitle_time = 5 if has_subtitles else 0  # 字幕処理時間
    bgm_time = 3 if has_bgm else 0  # BGM処理時間

    return base_time + segment_overhead + subtitle_time + bgm_time


def validate_cut_segments(cut_segments: List[Dict[str, Any]], video_duration: float, max_total_duration: float = 90) -> Dict[str, Any]:
    """カットセグメントの妥当性を検証"""
    errors = []
    warnings = []
    total_duration = 0

    for i, segment in enumerate(cut_segments):
        start_time = segment.get("start_time", 0)
        end_time = segment.get("end_time", 0)

        # 基本的な検証
        if start_time < 0:
            errors.append(f"セグメント{i+1}: 開始時間が負の値です")

        if end_time <= start_time:
            errors.append(f"セグメント{i+1}: 終了時間が開始時間以下です")

        if start_time >= video_duration:
            errors.append(f"セグメント{i+1}: 開始時間が動画長を超えています")

        if end_time > video_duration:
            warnings.append(f"セグメント{i+1}: 終了時間が動画長を超えています")

        # セグメント長の確認
        segment_duration = end_time - start_time
        total_duration += segment_duration

        if segment_duration < 1:
            warnings.append(f"セグメント{i+1}: セグメントが短すぎます（{segment_duration:.1f}秒）")

        if segment_duration > 30:
            warnings.append(f"セグメント{i+1}: セグメントが長すぎます（{segment_duration:.1f}秒）")

    # 全体の長さチェック
    if total_duration > max_total_duration:
        warnings.append(f"総時間が長すぎます（{total_duration:.1f}秒 > {max_total_duration}秒）")

    if total_duration < 10:
        warnings.append(f"総時間が短すぎます（{total_duration:.1f}秒）")

    return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings, "total_duration": total_duration, "num_segments": len(cut_segments)}
