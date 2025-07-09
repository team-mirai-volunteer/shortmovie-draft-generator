#!/usr/bin/env python3
"""
動画カットスクリプト
動画と開始時間、終了時間を受け取り、その通りにカットするPythonスクリプト
"""

import ffmpeg
import sys
import os
from pathlib import Path
from typing import Union


def cut_video(input_path: Union[str, Path], output_path: Union[str, Path], start_time: float, end_time: float, overwrite: bool = True) -> bool:
    """
    動画をカットする

    Args:
        input_path: 入力動画ファイルのパス
        output_path: 出力動画ファイルのパス
        start_time: 開始時間（秒）
        end_time: 終了時間（秒）
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

        if start_time < 0:
            print("エラー: 開始時間は0以上である必要があります")
            return False

        if end_time <= start_time:
            print("エラー: 終了時間は開始時間より大きい必要があります")
            return False

        duration = end_time - start_time

        output_path.parent.mkdir(parents=True, exist_ok=True)

        stream = ffmpeg.input(str(input_path), ss=start_time, t=duration)

        if overwrite:
            stream = ffmpeg.output(stream, str(output_path))
        else:
            if output_path.exists():
                print(f"エラー: 出力ファイルが既に存在します: {output_path}")
                return False
            stream = ffmpeg.output(stream, str(output_path))

        ffmpeg.run(stream, quiet=True, overwrite_output=overwrite)

        print(f"動画カット完了: {output_path}")
        print(f"カット範囲: {start_time}秒 - {end_time}秒 (長さ: {duration}秒)")
        return True

    except ffmpeg.Error as e:
        print(f"FFmpegエラー: {e}")
        return False
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return False


def main():
    """コマンドライン実行用のメイン関数"""
    if len(sys.argv) != 5:
        print("使用方法: python 01_video_cut.py <入力ファイル> <出力ファイル> <開始時間> <終了時間>")
        print("例: python 01_video_cut.py input.mp4 output.mp4 10.5 30.2")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        start_time = float(sys.argv[3])
        end_time = float(sys.argv[4])
    except ValueError:
        print("エラー: 開始時間と終了時間は数値で指定してください")
        sys.exit(1)

    success = cut_video(input_file, output_file, start_time, end_time)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
