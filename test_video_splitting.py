#!/usr/bin/env python3
"""
動画分割機能のテストスクリプト
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from lib.video_splitting.csv_parser import parse_qa_csv
from lib.video_splitting.whisper_analyzer import load_whisper_transcript
from lib.video_splitting.text_matcher import match_qa_with_whisper


def test_data_loading():
    """データ読み込みのテスト"""
    print("=== データ読み込みテスト ===")

    csv_path = "/home/ubuntu/attachments/42d2cd54-b84a-4545-97cb-a36fd26acd03/studio_results_20250710_2021.csv"
    whisper_json = "whisper_output/aianno_test.json"

    try:
        qa_segments = parse_qa_csv(csv_path)
        print(f"✓ CSVデータ読み込み成功: {len(qa_segments)}件")

        if qa_segments:
            sample = qa_segments[0]
            print(f"  サンプル - ID: {sample['id']}")
            print(f"  Query: {sample['query'][:50]}...")
            print(f"  QText: {sample['qtext'][:50]}...")
            print(f"  Text: {sample['text'][:50]}...")
    except Exception as e:
        print(f"✗ CSVデータ読み込み失敗: {e}")
        return False

    try:
        whisper_segments = load_whisper_transcript(whisper_json)
        print(f"✓ Whisperデータ読み込み成功: {len(whisper_segments)}件")

        if whisper_segments:
            sample = whisper_segments[0]
            print(f"  サンプル - 時間: {sample['start']:.1f}s - {sample['end']:.1f}s")
            print(f"  テキスト: {sample['text'][:50]}...")
    except Exception as e:
        print(f"✗ Whisperデータ読み込み失敗: {e}")
        return False

    return True


def test_matching():
    """マッチングアルゴリズムのテスト"""
    print("\n=== マッチングテスト ===")

    csv_path = "/home/ubuntu/attachments/42d2cd54-b84a-4545-97cb-a36fd26acd03/studio_results_20250710_2021.csv"
    whisper_json = "whisper_output/aianno_test.json"

    try:
        qa_segments = parse_qa_csv(csv_path)
        whisper_segments = load_whisper_transcript(whisper_json)

        test_qa = qa_segments[:10]
        matches = match_qa_with_whisper(test_qa, whisper_segments, confidence_threshold=0.3)

        matched_count = sum(1 for m in matches if m["whisper_segment"] is not None)
        print(f"✓ マッチング実行成功: {matched_count}/{len(matches)}件マッチ")

        for i, match in enumerate(matches[:3]):
            print(f"\n  マッチ {i+1}:")
            print(f"    Query: {match['qa']['query'][:50]}...")
            if match["whisper_segment"]:
                print(f"    マッチ時間: {match['whisper_segment']['start']:.1f}s - {match['whisper_segment']['end']:.1f}s")
                print(f"    信頼度: {match['confidence']:.3f}")
                print(f"    マッチタイプ: {match['match_type']}")
            else:
                print(f"    推定時間: {match['estimated_timing']['start']:.1f}s - {match['estimated_timing']['end']:.1f}s")
                print(f"    マッチタイプ: {match['match_type']}")

        return True
    except Exception as e:
        print(f"✗ マッチングテスト失敗: {e}")
        return False


def main():
    print("動画分割機能テスト開始")

    if not test_data_loading():
        print("データ読み込みテストに失敗しました")
        sys.exit(1)

    if not test_matching():
        print("マッチングテストに失敗しました")
        sys.exit(1)

    print("\n✓ すべてのテストが成功しました")


if __name__ == "__main__":
    main()
