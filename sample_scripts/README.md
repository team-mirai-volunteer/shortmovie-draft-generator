# 動画処理サンプルスクリプト

このディレクトリには、動画処理のためのPythonサンプルスクリプトが含まれています。

## 前提条件

- Python 3.8以上
- ffmpeg-python (`pip install ffmpeg-python`)
- FFmpegがシステムにインストールされていること

## スクリプト一覧

### 1. 動画カット (`01_video_cut.py`)

動画と開始時間、終了時間を受け取り、その通りにカットするスクリプト。

```bash
python 01_video_cut.py <入力ファイル> <出力ファイル> <開始時間> <終了時間>
```

**例:**
```bash
python 01_video_cut.py input.mp4 output.mp4 10.5 30.2
```

### 2. テキストオーバーレイ (`02_text_overlay.py`)

動画の冒頭0.1秒に黒縁取りの黄色い文字で強烈なメッセージを重ねるスクリプト。

```bash
python 02_text_overlay.py <入力ファイル> <出力ファイル> <テキスト> [表示時間]
```

**例:**
```bash
python 02_text_overlay.py input.mp4 output.mp4 "衝撃の事実！" 0.1
```

### 3. アスペクト比変換 (`03_aspect_ratio_convert.py`)

横長動画をTikTokの縦長画面（9:16）にはめるスクリプト。

```bash
python 03_aspect_ratio_convert.py <入力ファイル> <出力ファイル> [幅] [高さ] [スケールモード]
```

**例:**
```bash
python 03_aspect_ratio_convert.py input.mp4 output.mp4 1080 1920 fit
```

**スケールモード:**
- `fit`: アスペクト比を維持して画面に収める（推奨）
- `fill`: 画面いっぱいに拡大（歪む可能性あり）

### 4. 字幕合成 (`04_subtitle_merge.py`)

SRTファイルと動画を受け取り字幕合成するスクリプト。

```bash
python 04_subtitle_merge.py <入力動画> <SRTファイル> <出力ファイル> [フォントサイズ] [位置]
```

**例:**
```bash
python 04_subtitle_merge.py input.mp4 subtitles.srt output.mp4 24 bottom
```

**位置オプション:**
- `bottom`: 下部（デフォルト）
- `top`: 上部
- `center`: 中央

## 使用例

### 完全なワークフロー例

```bash
# 1. 元動画から必要な部分をカット
python 01_video_cut.py original.mp4 cut.mp4 30 90

# 2. カットした動画にインパクトのあるテキストを追加
python 02_text_overlay.py cut.mp4 with_text.mp4 "必見！驚きの結果" 0.1

# 3. TikTok用の縦長フォーマットに変換
python 03_aspect_ratio_convert.py with_text.mp4 vertical.mp4 1080 1920 fit

# 4. 字幕を追加
python 04_subtitle_merge.py vertical.mp4 subtitles.srt final.mp4 28 bottom
```

## 注意事項

- 大きなファイルの処理には時間がかかる場合があります
- 出力ファイルが既に存在する場合、デフォルトで上書きされます
- エラーが発生した場合は、FFmpegのインストール状況と入力ファイルの形式を確認してください

## トラブルシューティング

### FFmpegが見つからない場合
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows
# https://ffmpeg.org/download.html からダウンロードしてPATHに追加
```

### Python依存関係のインストール
```bash
pip install ffmpeg-python
```
