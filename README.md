# ショート動画企画案生成ツール

YouTube動画を解析して、ショート動画の企画案とカット案を自動生成するAIツールです。

## 概要

このツールは、YouTube動画のURLを入力するだけで、以下を自動生成します：
- ショート動画の企画案（複数パターン）
- 詳細なカット案（タイムスタンプ付き）
- 編集用の資料（PowerPoint、Word、PDF形式）

## 主な機能

- **YouTube動画解析**: 動画の内容を自動で解析・要約
- **AI企画案生成**: OpenAI GPTを使用した多様な企画案の提案
- **カット案作成**: 具体的な開始・終了時間付きのカット指示
- **資料出力**: 編集作業に使える各種フォーマットでの出力
- **ユーザー認証**: セキュアなログイン機能

## 必要な環境

- **Python**: 3.11.3（厳密にこのバージョンが必要）
- **パッケージマネージャー**: rye
- **OpenAI APIキー**: GPT利用のため必須

## セットアップ手順

### 1. ryeのインストール

```bash
# macOS/Linux
curl -sSf https://rye.astral.sh/get | bash

# Windows
# https://rye.astral.sh/guide/installation/ を参照
```

### 2. プロジェクトのセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/team-mirai-volunteer/shortmovie-draft-generator.git
cd shortmovie-draft-generator

# 依存関係をインストール
rye sync
```

### 3. 環境変数の設定

```bash
# 環境変数ファイルを作成
cp .env.example .env.local
```

`.env.local`ファイルを編集して、OpenAI APIキーを設定：

```
OPENAI_API_KEY="your_openai_api_key_here"
```

**OpenAI APIキーの取得方法:**
1. [OpenAI Platform](https://platform.openai.com/)にアクセス
2. アカウント作成・ログイン
3. API Keys セクションでキーを生成
4. 生成されたキーを上記ファイルに設定

### 4. 認証設定（オプション）

認証設定を変更する場合は、`authenticator.yaml`ファイルを編集してください。

## 使用方法

### アプリケーションの起動

```bash
rye run dev
```

起動後、ブラウザで以下のURLにアクセス：
- ローカル: http://localhost:8501

### 基本的な使い方

1. **ログイン**: 認証情報を入力してログイン
2. **YouTube動画生成ページ**に移動
3. **YouTube URL**を入力
4. **生成開始**ボタンをクリック
5. **結果の確認**: 生成された企画案とカット案を確認
6. **ダウンロード**: 必要に応じて資料をダウンロード

## トラブルシューティング

### よくある問題

**Q: `rye sync`でエラーが発生する**
A: Python 3.11.3がインストールされているか確認してください。ryeが自動でインストールしない場合は、手動でインストールが必要です。

**Q: OpenAI APIエラーが発生する**
A: 
- APIキーが正しく設定されているか確認
- OpenAIアカウントに十分なクレジットがあるか確認
- APIキーに適切な権限があるか確認

**Q: アプリケーションが起動しない**
A:
- ポート8501が他のプロセスで使用されていないか確認
- 依存関係が正しくインストールされているか確認（`rye sync`を再実行）

**Q: YouTube動画の処理でエラーが発生する**
A:
- 動画が公開されているか確認
- 動画にトランスクリプト（字幕）が利用可能か確認
- ネットワーク接続を確認

### ログの確認

問題が発生した場合は、コンソールに表示されるエラーメッセージを確認してください。

## 開発者向け情報

### プロジェクト構造

```
src/
├── streamlit/          # Webアプリケーション
│   ├── main.py        # メインアプリケーション
│   └── pages/         # 各ページのコンポーネント
├── lib/youtube/       # YouTube処理ライブラリ
├── agent_sdk/         # AI エージェントフレームワーク
└── setting.py         # 設定管理
```

### 開発用コマンド

```bash
# テスト実行
rye run test

# コードフォーマット
rye run black .

# データベースマイグレーション
rye run migrate
```

## ライセンス

このプロジェクトのライセンスについては、LICENSEファイルを参照してください。

## 貢献

プロジェクトへの貢献を歓迎します。Issue報告やPull Requestをお気軽にお送りください。
