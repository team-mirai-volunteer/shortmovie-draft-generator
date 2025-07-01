# -*- coding: utf-8 -*-
"""YouTube動画ダウンロード用ツール"""

import os
import tempfile
from pathlib import Path
from typing import Optional
import yt_dlp
from urllib.parse import urlparse, parse_qs
from src.agent_sdk.schemas.youtube import VideoInfo, YouTubeDownloadResult


def cleanup_cookie_file(cookie_file_path: str) -> None:
    """一時的なCookieファイルを削除

    Args:
        cookie_file_path: 削除するCookieファイルのパス
    """
    try:
        if cookie_file_path and os.path.exists(cookie_file_path):
            os.unlink(cookie_file_path)
    except Exception as e:
        print(f"Cookieファイル削除エラー: {e}")


default_ydl_opts = {
    "verbose": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["mweb"],
            "rustypipe_bg_pot_cache": "1",
        }
    },
}


def extract_video_id_from_url(url: str) -> str:
    """YouTube URLから動画IDを抽出"""
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "youtube.com/watch" in url:
        parsed = urlparse(url)
        return parse_qs(parsed.query).get("v", [""])[0]
    elif "youtube.com/embed/" in url:
        return url.split("youtube.com/embed/")[1].split("?")[0]
    else:
        # 動画IDが直接渡された場合
        return url


def download_youtube_video(
    video_url: str, output_dir: Optional[str] = None, include_audio: bool = True, video_quality: str = "720p", cookies: Optional[str] = None
) -> YouTubeDownloadResult:
    """YouTube動画をダウンロードする

    Args:
        video_url: YouTube動画のURL
        output_dir: 出力ディレクトリ（指定しない場合は一時ディレクトリ）
        include_audio: 音声ファイルも別途ダウンロードするかどうか
        video_quality: 動画品質（720p, 1080p等）
        cookies: YouTubeのCookies（Netscape形式またはブラウザからエクスポートした形式）

    Returns:
        ダウンロード結果の辞書
    """
    try:
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 動画ID抽出
        video_id = extract_video_id_from_url(video_url)
        if not video_id:
            return {"success": False, "error": "無効なYouTube URLです", "video_id": None, "video_path": None, "audio_path": None, "metadata": None}

        # yt-dlp設定
        ydl_opts = default_ydl_opts.copy()
        ydl_opts.update(
            {
                "outtmpl": str(output_path / f"{video_id}_%(title)s.%(ext)s"),
                "format": f"best[height<={video_quality[:-1]}]",  # 720p -> 720
                "writeinfojson": True,  # メタデータも保存
                "writesubtitles": False,  # 字幕は別途取得
                "writeautomaticsub": False,
            }
        )

        # Cookiesが提供されている場合は追加
        cookie_file_path = None
        if cookies:
            # 一時的なCookieファイルを作成
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as cookie_file:
                cookie_file.write(cookies)
                cookie_file_path = cookie_file.name
                ydl_opts["cookiefile"] = cookie_file_path

        video_path = None
        audio_path = None
        metadata = {}

        # 動画ダウンロード
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # メタデータ取得
            info = ydl.extract_info(video_url, download=False)
            metadata = {
                "video_id": video_id,
                "title": info.get("title", ""),
                "description": info.get("description", ""),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", ""),
                "upload_date": info.get("upload_date", ""),
                "view_count": info.get("view_count", 0),
                "like_count": info.get("like_count", 0),
                "thumbnail": info.get("thumbnail", ""),
                "webpage_url": info.get("webpage_url", video_url),
            }

            # 動画ダウンロード実行
            ydl.download([video_url])

            # ダウンロードされたファイルを探す
            for file_path in output_path.glob(f"{video_id}_*"):
                if file_path.suffix.lower() in [".mp4", ".mkv", ".webm", ".avi"]:
                    video_path = str(file_path)
                    break

        # 音声ファイルも別途ダウンロード（必要に応じて）
        if include_audio:
            audio_opts = {
                "outtmpl": str(output_path / f"{video_id}_audio.%(ext)s"),
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }

            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([video_url])

                # 音声ファイルを探す
                for file_path in output_path.glob(f"{video_id}_audio.*"):
                    if file_path.suffix.lower() in [".mp3", ".wav", ".m4a"]:
                        audio_path = str(file_path)
                        break

        # Cookieファイルのクリーンアップ
        if cookie_file_path:
            cleanup_cookie_file(cookie_file_path)

        return YouTubeDownloadResult(success=True, video_path=video_path, audio_path=audio_path, metadata=VideoInfo(**metadata) if metadata else None)

    except Exception as e:
        # エラーが発生した場合もCookieファイルをクリーンアップ
        if "cookie_file_path" in locals() and cookie_file_path:
            cleanup_cookie_file(cookie_file_path)
        return YouTubeDownloadResult(success=False, error=f"動画ダウンロードエラー: {str(e)}")


def get_video_info(video_url: str, cookies: Optional[str] = None) -> YouTubeDownloadResult:
    """YouTube動画の情報を取得（ダウンロードなし）

    Args:
        video_url: YouTube動画のURL
        cookies: YouTubeのCookies（Netscape形式またはブラウザからエクスポートした形式）

    Returns:
        動画情報の辞書
    """
    try:
        video_id = extract_video_id_from_url(video_url)
        if not video_id:
            return YouTubeDownloadResult(success=False, error="無効なYouTube URLです")

        ydl_opts = default_ydl_opts.copy()

        # Cookiesが提供されている場合は追加
        cookie_file_path = None
        if cookies:
            # 一時的なCookieファイルを作成
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as cookie_file:
                cookie_file.write(cookies)
                cookie_file_path = cookie_file.name
                ydl_opts["cookiefile"] = cookie_file_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            video_info = {
                "video_id": video_id,
                "title": info.get("title", ""),
                "description": info.get("description", ""),
                "duration": info.get("duration", 0),
                "duration_string": info.get("duration_string", ""),
                "uploader": info.get("uploader", ""),
                "upload_date": info.get("upload_date", ""),
                "view_count": info.get("view_count", 0),
                "like_count": info.get("like_count", 0),
                "thumbnail": info.get("thumbnail", ""),
                "webpage_url": info.get("webpage_url", video_url),
                "tags": info.get("tags", []),
                "categories": info.get("categories", []),
                "availability": info.get("availability", ""),
                "age_limit": info.get("age_limit", 0),
            }

            # Cookieファイルのクリーンアップ
            if cookie_file_path:
                cleanup_cookie_file(cookie_file_path)

            return YouTubeDownloadResult(success=True, metadata=VideoInfo(**video_info))

    except Exception as e:
        # エラーが発生した場合もCookieファイルをクリーンアップ
        if "cookie_file_path" in locals() and cookie_file_path:
            cleanup_cookie_file(cookie_file_path)
        return YouTubeDownloadResult(success=False, error=f"動画情報取得エラー: {str(e)}")


def cleanup_temp_files(file_paths: list) -> bool:
    """一時ファイルを削除

    Args:
        file_paths: 削除するファイルパスのリスト

    Returns:
        削除が成功したかどうか
    """
    try:
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        return True
    except Exception as e:
        print(f"ファイル削除エラー: {e}")
        return False
