#!/usr/bin/env python3
"""
テキストオーバーレイスクリプト
動画の冒頭0.1秒に黒縁取りの黄色い文字で強烈なメッセージを重ねることでサムネイルで目を引くようにするスクリプト
"""

import ffmpeg
import sys
import os
from pathlib import Path
from typing import Union


def add_text_overlay(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    text: str,
    duration: float = 0.1,
    font_size: int = 48,
    font_color: str = "yellow",
    border_color: str = "black",
    border_width: int = 3,
    position: str = "center",
    overwrite: bool = True,
) -> bool:
    """
    動画の冒頭に黒縁取りの黄色いテキストを追加する

    Args:
        input_path: 入力動画ファイルのパス
        output_path: 出力動画ファイルのパス
        text: 表示するテキスト
        duration: テキスト表示時間（秒）
        font_size: フォントサイズ
        font_color: フォント色
        border_color: 縁取り色
        border_width: 縁取りの太さ
        position: テキスト位置 ("center", "top", "bottom")
        overwrite: 出力ファイルが存在する場合に上書きするか

    Returns:
        bool: 成功した場合True、失敗した場合False
    """
    try:
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            print(f"エラー: 入力ファイルが見つかりません: {input_path}")
            return False

        if duration <= 0:
            print("エラー: 表示時間は0より大きい必要があります")
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)

        position_map = {"center": "(w-text_w)/2:(h-text_h)/2", "top": "(w-text_w)/2:50", "bottom": "(w-text_w)/2:h-text_h-50"}

        if position not in position_map:
            position = "center"

        text_position = position_map[position]

        drawtext_filter = (
            f"drawtext=text='{text}'"
            f":fontsize={font_size}"
            f":fontcolor={font_color}"
            f":bordercolor={border_color}"
            f":borderw={border_width}"
            f":x={text_position.split(':')[0]}"
            f":y={text_position.split(':')[1]}"
            f":enable='between(t,0,{duration})'"
        )

        input_stream = ffmpeg.input(str(input_path))

        output_stream = ffmpeg.filter(
            input_stream,
            "drawtext",
            text=text,
            fontsize=font_size,
            fontcolor=font_color,
            bordercolor=border_color,
            borderw=border_width,
            x=text_position.split(":")[0],
            y=text_position.split(":")[1],
            enable=f"between(t,0,{duration})",
        )

        output_stream = ffmpeg.output(output_stream, str(output_path))

        ffmpeg.run(output_stream, quiet=True, overwrite_output=overwrite)

        print(f"テキストオーバーレイ完了: {output_path}")
        print(f"テキスト: '{text}' (表示時間: {duration}秒)")
        return True

    except ffmpeg.Error as e:
        print(f"FFmpegエラー: {e}")
        return False
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return False


def main():
    """コマンドライン実行用のメイン関数"""
    if len(sys.argv) < 4:
        print("使用方法: python 02_text_overlay.py <入力ファイル> <出力ファイル> <テキスト> [表示時間]")
        print("例: python 02_text_overlay.py input.mp4 output.mp4 '衝撃の事実！' 0.1")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    text = sys.argv[3]

    duration = 0.1
    if len(sys.argv) >= 5:
        try:
            duration = float(sys.argv[4])
        except ValueError:
            print("エラー: 表示時間は数値で指定してください")
            sys.exit(1)

    success = add_text_overlay(input_file, output_file, text, duration)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
