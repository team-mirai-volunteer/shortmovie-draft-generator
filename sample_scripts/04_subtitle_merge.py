#!/usr/bin/env python3
"""
字幕合成スクリプト
SRTと動画を受け取り字幕合成するPythonスクリプト
"""

import ffmpeg
import sys
import os
from pathlib import Path
from typing import Union, List, Optional
import re


class SRTParser:
    """SRTファイルのパーサー"""

    @staticmethod
    def parse_srt(srt_path: Union[str, Path]) -> List[dict]:
        """
        SRTファイルを解析して字幕データを取得する

        Args:
            srt_path: SRTファイルのパス

        Returns:
            List[dict]: 字幕データのリスト
        """
        subtitles = []

        try:
            with open(srt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            subtitle_blocks = re.split(r"\n\s*\n", content)

            for block in subtitle_blocks:
                lines = block.strip().split("\n")
                if len(lines) < 3:
                    continue

                index = lines[0].strip()
                time_line = lines[1].strip()
                text_lines = lines[2:]

                time_match = re.match(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})", time_line)

                if not time_match:
                    continue

                start_h, start_m, start_s, start_ms = map(int, time_match.groups()[:4])
                end_h, end_m, end_s, end_ms = map(int, time_match.groups()[4:])

                start_time = start_h * 3600 + start_m * 60 + start_s + start_ms / 1000
                end_time = end_h * 3600 + end_m * 60 + end_s + end_ms / 1000

                text = "\n".join(text_lines).strip()

                subtitles.append({"index": int(index), "start_time": start_time, "end_time": end_time, "text": text})

        except Exception as e:
            print(f"SRTファイル解析エラー: {e}")
            return []

        return subtitles

    @staticmethod
    def create_temp_srt(subtitles: List[dict], temp_path: Union[str, Path]) -> bool:
        """
        字幕データから一時的なSRTファイルを作成する

        Args:
            subtitles: 字幕データのリスト
            temp_path: 一時ファイルのパス

        Returns:
            bool: 成功した場合True
        """
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                for subtitle in subtitles:
                    start_time = subtitle["start_time"]
                    end_time = subtitle["end_time"]

                    start_h = int(start_time // 3600)
                    start_m = int((start_time % 3600) // 60)
                    start_s = int(start_time % 60)
                    start_ms = int((start_time % 1) * 1000)

                    end_h = int(end_time // 3600)
                    end_m = int((end_time % 3600) // 60)
                    end_s = int(end_time % 60)
                    end_ms = int((end_time % 1) * 1000)

                    f.write(f"{subtitle['index']}\n")
                    f.write(f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> ")
                    f.write(f"{end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}\n")
                    f.write(f"{subtitle['text']}\n\n")

            return True
        except Exception as e:
            print(f"一時SRTファイル作成エラー: {e}")
            return False


def merge_subtitles(
    input_video_path: Union[str, Path],
    srt_path: Union[str, Path],
    output_path: Union[str, Path],
    font_size: int = 24,
    font_color: str = "white",
    border_color: str = "black",
    border_width: int = 2,
    position: str = "bottom",
    overwrite: bool = True,
) -> bool:
    """
    動画にSRT字幕を合成する

    Args:
        input_video_path: 入力動画ファイルのパス
        srt_path: SRTファイルのパス
        output_path: 出力動画ファイルのパス
        font_size: フォントサイズ
        font_color: フォント色
        border_color: 縁取り色
        border_width: 縁取りの太さ
        position: 字幕位置 ("bottom", "top", "center")
        overwrite: 出力ファイルが存在する場合に上書きするか

    Returns:
        bool: 成功した場合True、失敗した場合False
    """
    try:
        input_video_path = Path(input_video_path)
        srt_path = Path(srt_path)
        output_path = Path(output_path)

        if not input_video_path.exists():
            print(f"エラー: 入力動画ファイルが見つかりません: {input_video_path}")
            return False

        if not srt_path.exists():
            print(f"エラー: SRTファイルが見つかりません: {srt_path}")
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)

        subtitles = SRTParser.parse_srt(srt_path)
        if not subtitles:
            print("エラー: SRTファイルから字幕データを取得できませんでした")
            return False

        print(f"字幕数: {len(subtitles)}個")

        input_stream = ffmpeg.input(str(input_video_path))

        position_map = {"bottom": "h-text_h-50", "top": "50", "center": "(h-text_h)/2"}

        if position not in position_map:
            position = "bottom"

        y_position = position_map[position]

        output_stream = ffmpeg.filter(
            input_stream,
            "subtitles",
            filename=str(srt_path),
            force_style=f"FontSize={font_size},PrimaryColour=&H{_color_to_hex(font_color)},OutlineColour=&H{_color_to_hex(border_color)},Outline={border_width}",
        )

        output_stream = ffmpeg.output(output_stream, str(output_path))

        ffmpeg.run(output_stream, quiet=True, overwrite_output=overwrite)

        print(f"字幕合成完了: {output_path}")
        print(f"合成した字幕数: {len(subtitles)}個")
        return True

    except ffmpeg.Error as e:
        print(f"FFmpegエラー: {e}")
        return False
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return False


def _color_to_hex(color: str) -> str:
    """色名をHEX値に変換する（簡易版）"""
    color_map = {"white": "FFFFFF", "black": "000000", "red": "0000FF", "green": "00FF00", "blue": "FF0000", "yellow": "00FFFF", "cyan": "FFFF00", "magenta": "FF00FF"}
    return color_map.get(color.lower(), "FFFFFF")


def main():
    """コマンドライン実行用のメイン関数"""
    if len(sys.argv) < 4:
        print("使用方法: python 04_subtitle_merge.py <入力動画> <SRTファイル> <出力ファイル> [フォントサイズ] [位置]")
        print("例: python 04_subtitle_merge.py input.mp4 subtitles.srt output.mp4 24 bottom")
        print("位置: bottom (下部), top (上部), center (中央)")
        sys.exit(1)

    input_video = sys.argv[1]
    srt_file = sys.argv[2]
    output_file = sys.argv[3]

    font_size = 24
    position = "bottom"

    if len(sys.argv) >= 5:
        try:
            font_size = int(sys.argv[4])
        except ValueError:
            print("エラー: フォントサイズは整数で指定してください")
            sys.exit(1)

    if len(sys.argv) >= 6:
        position = sys.argv[5]
        if position not in ["bottom", "top", "center"]:
            print("エラー: 位置は 'bottom', 'top', 'center' のいずれかで指定してください")
            sys.exit(1)

    success = merge_subtitles(input_video, srt_file, output_file, font_size=font_size, position=position)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
