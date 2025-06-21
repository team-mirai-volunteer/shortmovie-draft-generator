# -*- coding: utf-8 -*-
"""YouTube動画シナリオ生成のためのContextクラス"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from ..schemas.youtube import VideoInfo, TranscriptChunk, Scenario, CutSegment


class YouTubeScenarioContext(BaseModel):
    """YouTube動画シナリオ生成のためのContext"""

    # Video metadata
    video_url: str = ""
    video_id: str = ""
    video_title: str = ""
    video_duration: float = 0.0
    video_duration_string: str = ""
    video_description: str = ""
    channel_name: str = ""
    upload_date: str = ""
    view_count: int = 0
    like_count: int = 0
    thumbnail: str = ""
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    availability: str = ""
    age_limit: int = 0

    # Transcript data
    transcript_chunks: List[TranscriptChunk] = Field(default_factory=list)
    processed_transcript: List[TranscriptChunk] = Field(default_factory=list)

    # Scenario generation
    generated_scenarios: List[Scenario] = Field(default_factory=list)
    selected_scenarios: List[str] = Field(default_factory=list)

    # Video processing
    downloaded_video_path: str = ""
    downloaded_audio_path: str = ""
    output_video_path: str = ""

    # Processing status
    is_video_downloaded: bool = False
    is_transcript_extracted: bool = False
    is_scenarios_generated: bool = False
    is_cuts_generated: bool = False
    is_video_processed: bool = False

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True

    def set_video_info(self, video_info: Dict[str, Any]):
        """動画基本情報を設定（video_info辞書から）"""
        self.video_id = video_info.get("video_id", "")
        self.video_title = video_info.get("title", "")
        self.video_duration = video_info.get("duration", 0.0)
        self.video_duration_string = video_info.get("duration_string", "")
        self.video_description = video_info.get("description", "")
        self.channel_name = video_info.get("uploader", "")
        self.video_url = video_info.get("webpage_url", "")
        self.upload_date = video_info.get("upload_date", "")
        self.view_count = video_info.get("view_count", 0)
        self.like_count = video_info.get("like_count", 0)
        self.thumbnail = video_info.get("thumbnail", "")
        self.tags = video_info.get("tags", [])
        self.categories = video_info.get("categories", [])
        self.availability = video_info.get("availability", "")
        self.age_limit = video_info.get("age_limit", 0)
        self.update_timestamp()

    def add_transcript_chunk(self, chunk: Dict[str, Any]):
        """字幕チャンクを追加"""
        self.transcript_chunks.append(chunk)
        self.update_timestamp()

    def set_transcript_chunks(self, chunks: List[Dict[str, Any]]):
        """字幕チャンクを一括設定"""
        self.transcript_chunks = chunks
        self.is_transcript_extracted = True
        self.update_timestamp()

    def set_processed_transcript(self, processed_chunks: List[Dict[str, Any]]):
        """処理済み字幕を設定"""
        self.processed_transcript = processed_chunks
        self.update_timestamp()

    def add_scenario(self, scenario: Dict[str, Any]):
        """生成されたシナリオを追加"""
        # cut_segmentsフィールドが存在しない場合は空のリストで初期化
        if "cut_segments" not in scenario:
            scenario["cut_segments"] = []
        self.generated_scenarios.append(scenario)
        self.update_timestamp()

    def add_scenarios(self, scenarios: List[Dict[str, Any]]):
        """複数のシナリオを一括追加"""
        for scenario in scenarios:
            # cut_segmentsフィールドが存在しない場合は空のリストで初期化
            if "cut_segments" not in scenario:
                scenario["cut_segments"] = []
        self.generated_scenarios.extend(scenarios)
        self.is_scenarios_generated = True
        self.update_timestamp()

    def set_scenarios(self, scenarios: List[Dict[str, Any]]):
        """シナリオを一括設定"""
        for scenario in scenarios:
            # cut_segmentsフィールドが存在しない場合は空のリストで初期化
            if "cut_segments" not in scenario:
                scenario["cut_segments"] = []
        self.generated_scenarios = scenarios
        self.is_scenarios_generated = True
        self.update_timestamp()

    def select_scenarios(self, scenario_indices: List[int]):
        """シナリオを選択"""
        self.selected_scenarios = [self.generated_scenarios[i]["title"] if i < len(self.generated_scenarios) else "" for i in scenario_indices]
        self.update_timestamp()

    def set_cut_segments(self, segments: List[Dict[str, Any]]):
        """カットセグメントを設定（レガシー用）"""
        self.cut_segments = segments
        self.is_cuts_generated = True
        self.update_timestamp()

    def add_cut_segments_to_scenario(self, scenario_title: str, segments: List[Dict[str, Any]]):
        """指定されたシナリオにカットセグメントを追加"""
        for scenario in self.generated_scenarios:
            if scenario.get("title") == scenario_title:
                if "cut_segments" not in scenario:
                    scenario["cut_segments"] = []
                scenario["cut_segments"].extend(segments)
                self.is_cuts_generated = True
                self.update_timestamp()
                return True
        return False

    def add_cut_segments_to_scenarios(self, segments_by_scenario: Dict[str, List[Dict[str, Any]]]):
        """複数のシナリオにカットセグメントを一括追加"""
        updated_count = 0
        for scenario_title, segments in segments_by_scenario.items():
            if self.add_cut_segments_to_scenario(scenario_title, segments):
                updated_count += 1
        return updated_count

    def get_cut_segments_for_scenario(self, scenario_title: str) -> List[Dict[str, Any]]:
        """指定されたシナリオのカットセグメントを取得"""
        for scenario in self.generated_scenarios:
            if scenario.get("title") == scenario_title:
                return scenario.get("cut_segments", [])
        return []

    def get_all_cut_segments(self) -> List[Dict[str, Any]]:
        """全シナリオのカットセグメントを取得（フラット化）"""
        all_segments = []
        for scenario in self.generated_scenarios:
            segments = scenario.get("cut_segments", [])
            for segment in segments:
                # シナリオ情報を付加
                segment_with_scenario = segment.copy()
                segment_with_scenario["scenario_title"] = scenario.get("title", "")
                all_segments.append(segment_with_scenario)
        return all_segments

    def set_video_paths(self, video_path: str, audio_path: str = ""):
        """ダウンロード済み動画パスを設定"""
        self.downloaded_video_path = video_path
        self.downloaded_audio_path = audio_path
        self.is_video_downloaded = True
        self.update_timestamp()

    def set_output_path(self, output_path: str):
        """出力動画パスを設定"""
        self.output_video_path = output_path
        self.is_video_processed = True
        self.update_timestamp()

    def get_selected_scenario_details(self) -> List[Dict[str, Any]]:
        """選択されたシナリオの詳細を取得"""
        return [scenario for scenario in self.generated_scenarios if scenario.get("title") in self.selected_scenarios]

    def get_transcript_text(self) -> str:
        """字幕テキストを結合して取得（生のtranscript_chunksを優先）"""
        # タイムスタンプの精度を保つため、生のtranscript_chunksを優先
        if self.transcript_chunks:
            return " ".join([chunk.get("text", "") for chunk in self.transcript_chunks])
        return " ".join([chunk.get("text", "") for chunk in self.processed_transcript])

    def get_processing_status(self) -> Dict[str, bool]:
        """処理ステータスを取得"""
        # シナリオ内のカットセグメントもチェック
        has_scenario_cuts = any(len(scenario.get("cut_segments", [])) > 0 for scenario in self.generated_scenarios)
        cuts_generated = self.is_cuts_generated or has_scenario_cuts

        return {
            "video_downloaded": self.is_video_downloaded,
            "transcript_extracted": self.is_transcript_extracted,
            "scenarios_generated": self.is_scenarios_generated,
            "cuts_generated": cuts_generated,
            "video_processed": self.is_video_processed,
        }

    def reset_processing_status(self):
        """処理ステータスをリセット"""
        self.is_video_downloaded = False
        self.is_transcript_extracted = False
        self.is_scenarios_generated = False
        self.is_cuts_generated = False
        self.is_video_processed = False
        self.update_timestamp()

    def update_timestamp(self):
        """最終更新時刻を更新"""
        self.last_updated = datetime.now()

    def initialize_with_transcript(self, video_info: Dict[str, Any], transcript_chunks: List[Dict[str, Any]]):
        """シナリオ生成用に、字幕付きでContextを初期化する"""
        self.set_video_info(video_info)
        self.set_transcript_chunks(transcript_chunks)

    def update_cut_segments_with_validation(self, segments: List[Dict[str, Any]]) -> bool:
        """カットセグメントを検証付きで更新する"""
        # セグメントの基本的な検証
        for segment in segments:
            start_time = segment.get("start_time", 0)
            end_time = segment.get("end_time", 0)

            if start_time < 0 or end_time <= start_time:
                return False

            if self.video_duration > 0 and end_time > self.video_duration:
                return False

        self.set_cut_segments(segments)
        return True

    def get_scenario_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """タイトルでシナリオを検索する"""
        for scenario in self.generated_scenarios:
            if scenario.get("title") == title:
                return scenario
        return None

    def get_processing_summary(self) -> str:
        """処理状況のサマリを取得する"""
        status = self.get_processing_status()
        completed_steps = sum(status.values())
        total_steps = len(status)

        summary_parts = []
        if status["transcript_extracted"]:
            summary_parts.append(f"字幕: {len(self.transcript_chunks)}チャンク")
        if status["scenarios_generated"]:
            summary_parts.append(f"企画案: {len(self.generated_scenarios)}件")
        if status["cuts_generated"]:
            # レガシーカットセグメントとシナリオ内カットセグメントの両方をカウント
            total_cuts = len(self.get_all_cut_segments())
            summary_parts.append(f"カット: {total_cuts}セグメント")

        progress = f"{completed_steps}/{total_steps}ステップ完了"
        details = ", ".join(summary_parts) if summary_parts else "未処理"

        return f"{progress} ({details})"

    def to_dict(self) -> Dict[str, Any]:
        """Context情報を辞書形式で返す"""
        # シナリオ内のカットセグメント数を計算
        scenario_cut_segments_count = sum(len(scenario.get("cut_segments", [])) for scenario in self.generated_scenarios)

        return {
            "video_url": self.video_url,
            "video_id": self.video_id,
            "video_title": self.video_title,
            "video_duration": self.video_duration,
            "video_description": self.video_description,
            "channel_name": self.channel_name,
            "transcript_chunks_count": len(self.transcript_chunks),
            "processed_transcript_count": len(self.processed_transcript),
            "generated_scenarios_count": len(self.generated_scenarios),
            "selected_scenarios": self.selected_scenarios,
            "scenario_cut_segments_count": scenario_cut_segments_count,
            "total_cut_segments_count": scenario_cut_segments_count,
            "processing_status": self.get_processing_status(),
            "processing_summary": self.get_processing_summary(),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }
