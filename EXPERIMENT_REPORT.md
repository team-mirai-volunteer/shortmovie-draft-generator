# 動画分割実験レポート

## 概要

CSVの`created_at`順序とWhisper時間軸の対応関係を考慮した改良版マッチングアルゴリズムを実装し、時系列制約と時系列ボーナススコアを組み合わせたアプローチで順序一致率を向上させる実験を実施しました。

**実験期間:** 2025年7月10日-11日  
**対象動画:** 25分のAI動画（aianno.mp4）  
**CSVデータ:** 2630件のQ&Aデータ（有効データ: 2306件）  

## 実験目的

1. CSVの時系列とWhisper音声解析結果のマッチング精度向上
2. 順序一致率の改善（53.1% → 100%を目標）
3. 質の高い動画断片の特定と共有
4. 完全なQ&Aセッションを含む動画の生成

## 技術実装

### 1. 基本的な動画分割システム

#### 実装したモジュール
- `src/lib/video_splitting/csv_parser.py` - CSVデータの解析
- `src/lib/video_splitting/whisper_analyzer.py` - Whisper音声解析結果の処理
- `src/lib/video_splitting/text_matcher.py` - テキストマッチングアルゴリズム
- `src/lib/video_splitting/video_splitter.py` - 動画分割の実行
- `src/scripts/split_video_from_csv.py` - メインスクリプト

#### 基本的なマッチングアルゴリズム
```python
def calculate_similarity_optimized(text1: str, text2: str) -> float:
    """SequenceMatcherとキーワードボーナスを組み合わせた類似度計算"""
    base_similarity = SequenceMatcher(None, text1, text2).ratio()
    
    keywords = ['質問', '回答', 'について', 'ですか', 'でしょうか', 'ありがとう']
    bonus = sum(0.05 for keyword in keywords if keyword in text1 and keyword in text2)
    
    return min(1.0, base_similarity + bonus)
```

### 2. 時系列制約付きマッチングアルゴリズム

#### 主要な改良点
1. **時系列制約**: 前回マッチより後の時間のみ候補とする厳格な単調性制約
2. **時系列ボーナス**: 適切な時間間隔（30-120秒）に最大ボーナスを付与
3. **重み付け**: テキスト類似度と時系列ボーナスの調整可能な組み合わせ

#### 実装された関数
```python
def match_qa_with_whisper_temporal(qa_segments, whisper_segments, 
                                  confidence_threshold=0.3, temporal_weight=0.2)
def find_best_whisper_match_temporal(qa, whisper_segments, normalized_whisper_texts, 
                                   used_indices, last_matched_time, temporal_weight)
def calculate_temporal_bonus(current_time, last_time)
```

#### 時系列ボーナス計算
```python
def calculate_temporal_bonus(current_time: float, last_time: float) -> float:
    if last_time < 0:
        return 0.1  # 最初のマッチには小さなボーナス
    
    time_gap = current_time - last_time
    
    if 30 <= time_gap <= 120:
        return 0.3      # 最適な間隔
    elif 10 <= time_gap < 30:
        return 0.2      # 短い間隔
    elif 120 < time_gap <= 300:
        return 0.1      # 長い間隔
    else:
        return 0.0      # 不適切な間隔
```

## 実験結果

### 1. 基本マッチング結果

**データ統計:**
- 総Q&Aデータ: 2630件
- 有効Q&Aデータ: 2306件（「回答できません」を除外）
- Whisperセグメント: 1110件
- 動画長: 25分

**信頼度閾値別マッチ数:**
- 信頼度 ≥ 0.3: 494件
- 信頼度 ≥ 0.4: 256件
- 信頼度 ≥ 0.5: 94件
- 信頼度 ≥ 0.6: 35件
- 信頼度 ≥ 0.7: 9件
- 信頼度 ≥ 0.8: 4件

**現実的なマッチ数:** 25分動画に対して35-94件が妥当

### 2. 時系列制約付きマッチング結果

**改善効果:**
- 順序一致率: 53.1% → **100%**
- 順序違反: 231件 → **0件**
- マッチ数: 494件 → 11-12件（品質重視）

**パラメータ別結果（temporal_weight）:**
- weight=0.1: 11件のマッチ
- weight=0.2: 12件のマッチ
- weight=0.3: 12件のマッチ

### 3. 生成された動画の分析

**動画ファイル統計:**
- 総生成動画数: 176件（test_output_optimized/）
- ファイルサイズ範囲: 85KB - 4.2MB
- 動画長範囲: 0.522秒 - 60.022秒

**動画カテゴリ分析:**
1. **短時間動画（0.5-3秒）**: 85KB-250KB
   - 高信頼度Whisperマッチ
   - 断片的な音声のみ
   - 完全なQ&Aセッションとしては不適切

2. **長時間動画（60秒）**: 4.2MB
   - 推定タイミングによる生成
   - 完全なQ&Aセッションを含む
   - 実用的な長さ

## 品質評価

### 1. 最高信頼度マッチ
- **信頼度**: 0.889
- **タイムスタンプ**: 712.0秒-713.0秒
- **質問**: 「質問です...」
- **Whisperテキスト**: 「の質問です...」

### 2. 完全なQ&Aセッション例の問題点
**ファイル**: `qa_0013_ef5f67e7_人口の年齢分布で高齢者が多いため被選挙権一人一票は結果的に.mp4`
- **動画長**: 60.022秒
- **ファイルサイズ**: 4.2MB
- **品質**: 1080x1920解像度、プロフェッショナルな映像

**⚠️ 重大な品質問題（ユーザーフィードバック）:**
1. **質問部分の欠如**: 質問が終わって回答のところだけ切り抜かれている
2. **内容不一致**: 動画の内容が想定と違う
3. **回答の不完全性**: 回答の末尾が切れている

**問題の原因分析:**
- 推定タイミングによる動画生成の精度不足
- Whisperマッチングなしでの時間範囲推定の限界
- Q&A全体を包含する適切な時間範囲の特定困難

## 技術的課題と解決策

### 1. 環境依存性の問題
**課題**: `ffmpeg`, `pandas`, `pydantic`の依存関係エラー
**解決策**: 
```bash
pip install ffmpeg-python pandas pydantic
```

### 2. モジュールインポートエラー
**課題**: `ModuleNotFoundError: No module named 'src'`
**解決策**: 
```python
sys.path.append(str(Path(__file__).parent.parent))
```

### 3. ファイル共有の問題
**課題**: 動画ファイルのアクセス権限とリンク生成
**解決策**: ファイル名の正規化とコピー処理

## 実験で使用したスクリプト

### 1. 分析スクリプト
- `high_confidence_analysis.py` - 信頼度別マッチ数分析
- `temporal_matching_comparison.py` - 時系列制約効果の比較
- `simple_temporal_test.py` - 時系列アルゴリズムの単体テスト

### 2. テストスクリプト
- `test_optimized_split.py` - 最適化された動画分割テスト
- `test_final_split.py` - 最終的な動画分割実行
- `test_timing_fix.py` - タイミング修正テスト

### 3. 実行コマンド例
```bash
# 基本的な動画分割
python src/scripts/split_video_from_csv.py \
  input.csv video.mp4 whisper.json output_dir \
  --confidence-threshold 0.3

# 時系列制約付きマッチング
python src/scripts/split_video_from_csv.py \
  input.csv video.mp4 whisper.json output_dir \
  --temporal-matching \
  --temporal-weight 0.2
```

## 結論と推奨事項

### 1. 成功した点
- 時系列制約により順序一致率100%を達成
- 動画分割システムの基本的な実装完了
- 176件の動画ファイル生成に成功

### 1.1 失敗した点
- **完全なQ&Aセッションの生成に失敗**:
  - 質問部分が欠如し、回答のみの切り抜きとなった
  - 動画内容が期待値と一致しない
  - 回答の末尾が切断される問題

### 2. 改善が必要な点
- マッチ数の大幅な減少（494件 → 12件）
- 短時間動画の実用性の低さ
- ファイル共有システムの安定性
- **動画品質の重大な問題**:
  - 質問部分の欠如（回答のみの切り抜き）
  - 動画内容と期待値の不一致
  - 回答の末尾切断

### 3. 次のステップの推奨事項

#### 短期的改善
1. **動画切り抜き範囲の改善**: 質問開始から回答終了まで完全に包含する時間範囲の特定
2. **バッファ時間の最適化**: 質問前後に適切なマージンを追加
3. **Whisperセグメント境界の精密化**: 発話開始・終了の正確な検出
4. **時系列制約の緩和**: より多くのマッチを許可する柔軟な制約
5. **中間長動画の生成**: 10-30秒の適切な長さの動画作成
6. **信頼度閾値の最適化**: 0.4-0.5での実用的なバランス

#### 長期的改善
1. **完全なQ&A境界検出**: 質問開始から回答終了まで正確に特定するアルゴリズム
2. **音声解析の精度向上**: Whisperの設定最適化と発話境界の精密検出
3. **マルチモーダルマッチング**: テキスト+音声+映像の統合
4. **ユーザーフィードバック機能**: 手動修正とアルゴリズム学習
5. **動画内容検証システム**: 生成された動画の品質自動チェック

## ファイル構成

### 生成されたファイル
```
test_output_optimized/          # 176個の分割動画
whisper_output/aianno_test.json # Whisper解析結果
split_report_full.json          # 詳細な処理レポート
preview_*.png                   # 動画プレビューフレーム
```

### 実装ファイル
```
src/lib/video_splitting/        # 動画分割ライブラリ
src/scripts/                    # 実行スクリプト
temporal_matching_comparison.py # 比較分析
high_confidence_analysis.py     # 信頼度分析
```

## Git情報

**PR**: https://github.com/team-mirai-volunteer/shortmovie-draft-generator/pull/4  
**ブランチ**: `devin/1752172497-video-splitting-script`  
**CI状況**: ✅ 全テスト通過  

## 連絡先とセッション情報

**Devinセッション**: https://app.devin.ai/sessions/8f9be64f6a8948c28d7ffea2f337a721  
**実装者**: @nishio  
**実験日**: 2025年7月10日-11日  

---

このレポートは次の作業者が実験を継続し、改善を行うための包括的な情報を提供しています。質問や詳細な説明が必要な場合は、上記のDevinセッションで確認できます。
