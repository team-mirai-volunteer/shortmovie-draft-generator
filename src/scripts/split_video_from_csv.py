#!/usr/bin/env python3
"""
CSVファイルとWhisper解析結果を基に動画を1問1答形式に分割するスクリプト
"""

import argparse
import sys
from pathlib import Path
import json
import time

sys.path.append(str(Path(__file__).parent.parent))

from lib.video_splitting.video_splitter import VideoSplitter


def main():
    parser = argparse.ArgumentParser(description="CSVファイルとWhisper解析結果を基に動画を1問1答形式に分割")
    parser.add_argument("csv_path", help="Q&AデータのCSVファイルパス")
    parser.add_argument("video_path", help="元動画ファイルパス")
    parser.add_argument("whisper_json", help="Whisper解析結果のJSONファイルパス")
    parser.add_argument("output_dir", help="分割動画の出力ディレクトリ")
    parser.add_argument("--confidence-threshold", type=float, default=0.3, help="テキストマッチングの信頼度閾値 (デフォルト: 0.3)")
    parser.add_argument("--report", help="処理結果レポートの出力パス", default="split_report.json")
    parser.add_argument("--dry-run", action="store_true", help="実際の動画分割を行わずマッチング結果のみ表示")
    parser.add_argument("--temporal-matching", action="store_true", help="時系列制約を考慮したマッチングを使用")
    parser.add_argument("--temporal-weight", type=float, default=0.2, help="時系列ボーナスの重み (デフォルト: 0.2)")

    args = parser.parse_args()

    for file_path, name in [(args.csv_path, "CSV"), (args.video_path, "動画"), (args.whisper_json, "Whisper JSON")]:
        if not Path(file_path).exists():
            print(f"エラー: {name}ファイルが見つかりません: {file_path}")
            sys.exit(1)

    print("=== 動画分割スクリプト ===")
    print(f"CSVファイル: {args.csv_path}")
    print(f"動画ファイル: {args.video_path}")
    print(f"Whisper JSON: {args.whisper_json}")
    print(f"出力ディレクトリ: {args.output_dir}")
    print(f"信頼度閾値: {args.confidence_threshold}")
    print()

    start_time = time.time()

    if args.dry_run:
        print("ドライランモード: マッチング結果のみ表示")
    else:
        splitter = VideoSplitter(args.video_path, args.output_dir)
        results = splitter.split_video_from_csv_and_whisper(
            args.csv_path, args.whisper_json, args.confidence_threshold,
            args.temporal_matching, args.temporal_weight
        )

        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        elapsed_time = time.time() - start_time

        print(f"\n=== 処理結果 ===")
        print(f"処理時間: {elapsed_time:.1f}秒")
        print(f"成功: {len(successful)}件")
        print(f"失敗: {len(failed)}件")

        if successful:
            avg_confidence = sum(r["confidence"] for r in successful) / len(successful)
            whisper_matched = sum(1 for r in successful if r["timing_source"] == "whisper")
            print(f"平均信頼度: {avg_confidence:.3f}")
            print(f"Whisperマッチ: {whisper_matched}/{len(successful)}件")

        if failed:
            print(f"\n失敗した項目 (最初の5件):")
            for item in failed[:5]:
                print(f"  - {item['index']}: {item['query'][:50]}... | エラー: {item['error']}")

        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n詳細レポート: {args.report}")


if __name__ == "__main__":
    main()
