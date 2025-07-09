#!/usr/bin/env python3
"""
アスペクト比変換スクリプト
横長動画をTikTokの縦長画面（9:16）にはめるPythonスクリプト
"""

import ffmpeg
import sys
import os
from pathlib import Path
from typing import Union, Tuple


def convert_to_vertical(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    target_width: int = 1080,
    target_height: int = 1920,
    background_color: str = "black",
    scale_mode: str = "fit",
    overwrite: bool = True,
) -> bool:
    """
    横長動画をTikTok用の縦長（9:16）に変換する

    Args:
        input_path: 入力動画ファイルのパス
        output_path: 出力動画ファイルのパス
        target_width: 出力動画の幅
        target_height: 出力動画の高さ
        background_color: 背景色
        scale_mode: スケールモード ("fit": アスペクト比維持, "fill": 画面いっぱい)
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

        output_path.parent.mkdir(parents=True, exist_ok=True)

        input_stream = ffmpeg.input(str(input_path))

        if scale_mode == "fit":
            scaled_stream = ffmpeg.filter(
                input_stream,
                "scale",
                width=f"if(gte(iw/ih,{target_width}/{target_height}),{target_width},-1)",
                height=f"if(gte(iw/ih,{target_width}/{target_height}),-1,{target_height})",
            )

            output_stream = ffmpeg.filter(scaled_stream, "pad", width=target_width, height=target_height, x="(ow-iw)/2", y="(oh-ih)/2", color=background_color)
        else:
            output_stream = ffmpeg.filter(input_stream, "scale", width=target_width, height=target_height)

        output_stream = ffmpeg.output(output_stream, str(output_path))

        ffmpeg.run(output_stream, quiet=True, overwrite_output=overwrite)

        print(f"アスペクト比変換完了: {output_path}")
        print(f"出力サイズ: {target_width}x{target_height} ({target_width/target_height:.2f}:1)")
        print(f"スケールモード: {scale_mode}")
        return True

    except ffmpeg.Error as e:
        print(f"FFmpegエラー: {e}")
        return False
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return False


def get_video_dimensions(video_path: Union[str, Path]) -> Tuple[int, int]:
    """
    動画の解像度を取得する

    Args:
        video_path: 動画ファイルのパス

    Returns:
        Tuple[int, int]: (幅, 高さ)
    """
    try:
        probe = ffmpeg.probe(str(video_path))
        video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
        if video_stream:
            return int(video_stream["width"]), int(video_stream["height"])
        return 0, 0
    except Exception:
        return 0, 0


def main():
    """コマンドライン実行用のメイン関数"""
    if len(sys.argv) < 3:
        print("使用方法: python 03_aspect_ratio_convert.py <入力ファイル> <出力ファイル> [幅] [高さ] [スケールモード]")
        print("例: python 03_aspect_ratio_convert.py input.mp4 output.mp4 1080 1920 fit")
        print("スケールモード: fit (アスペクト比維持) または fill (画面いっぱい)")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    target_width = 1080
    target_height = 1920
    scale_mode = "fit"

    if len(sys.argv) >= 4:
        try:
            target_width = int(sys.argv[3])
        except ValueError:
            print("エラー: 幅は整数で指定してください")
            sys.exit(1)

    if len(sys.argv) >= 5:
        try:
            target_height = int(sys.argv[4])
        except ValueError:
            print("エラー: 高さは整数で指定してください")
            sys.exit(1)

    if len(sys.argv) >= 6:
        scale_mode = sys.argv[5]
        if scale_mode not in ["fit", "fill"]:
            print("エラー: スケールモードは 'fit' または 'fill' で指定してください")
            sys.exit(1)

    width, height = get_video_dimensions(input_file)
    if width > 0 and height > 0:
        print(f"入力動画サイズ: {width}x{height} ({width/height:.2f}:1)")

    success = convert_to_vertical(input_file, output_file, target_width, target_height, scale_mode=scale_mode)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
