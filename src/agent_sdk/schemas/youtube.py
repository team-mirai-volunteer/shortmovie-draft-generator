# -*- coding: utf-8 -*-
"""YouTube-related schemas for video processing and scenario generation."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class VideoInfo(BaseModel):
    """YouTube video metadata."""

    video_id: str
    title: str
    duration: float = 0.0
    duration_string: str = ""
    description: str = ""
    uploader: str = ""
    channel_name: str = ""
    webpage_url: str = ""
    upload_date: str = ""
    view_count: int = 0
    like_count: int = 0
    thumbnail: str = ""
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    availability: str = ""
    age_limit: int = 0


class TranscriptChunk(BaseModel):
    """Individual transcript chunk with timing."""

    text: str
    start: float
    duration: float

    @property
    def end(self) -> float:
        """End time of the chunk."""
        return self.start + self.duration

    @validator("start", "duration")
    def validate_timing(cls, v):
        if v < 0:
            raise ValueError("Timing values must be non-negative")
        return v


class ProcessedTranscript(BaseModel):
    """Processed transcript with metadata."""

    chunks: List[TranscriptChunk]
    language: str = "ja"
    total_duration: float = 0.0
    processing_info: Dict[str, Any] = Field(default_factory=dict)

    @validator("chunks")
    def validate_chunks_order(cls, v):
        """Ensure chunks are in chronological order."""
        for i in range(1, len(v)):
            if v[i].start < v[i - 1].start:
                raise ValueError("Transcript chunks must be in chronological order")
        return v


class CutSegment(BaseModel):
    """Video cut segment with timing and content."""

    start_time: float
    end_time: float
    content: str = ""
    purpose: str = ""
    editing_notes: str = ""

    @property
    def duration(self) -> float:
        """Duration of the segment."""
        return self.end_time - self.start_time

    @validator("end_time")
    def validate_end_after_start(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be greater than start_time")
        return v

    @validator("start_time", "end_time")
    def validate_positive_times(cls, v):
        if v < 0:
            raise ValueError("Time values must be non-negative")
        return v


class SubtitleItem(BaseModel):
    """Individual subtitle item with timing and formatted text."""
    
    start_time: float
    end_time: float
    text: str
    line_number: int = 1
    
    @property
    def duration(self) -> float:
        """Duration of the subtitle display."""
        return self.end_time - self.start_time
    
    @validator("end_time")
    def validate_end_after_start(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be greater than start_time")
        return v
    
    @validator("start_time", "end_time")
    def validate_positive_times(cls, v):
        if v < 0:
            raise ValueError("Time values must be non-negative")
        return v
    
    @validator("text")
    def validate_text_length(cls, v):
        """Ensure text is appropriate for 2-line display."""
        # 改行を除いた実際の文字数をチェック
        actual_length = len(v.replace('\n', ''))
        if actual_length > 60:  # 短文制限
            raise ValueError("Subtitle text should be concise (max 60 chars excluding newlines)")
        return v


class Scenario(BaseModel):
    """Video scenario/plan definition."""

    title: str
    first_impact: str = ""
    last_conclusion: str = ""
    summary: str = ""
    hook_strategy: str = ""
    target_audience: str = ""
    estimated_engagement: str = ""
    time_start: Optional[str] = None
    estimated_duration: float = 60.0
    content_type: str = "short"
    cut_segments: List[CutSegment] = Field(default_factory=list)
    subtitles: List[SubtitleItem] = Field(default_factory=list)

    @validator("estimated_duration")
    def validate_duration(cls, v):
        if v <= 0 or v > 300:  # Max 5 minutes
            raise ValueError("Duration must be between 0 and 300 seconds")
        return v
    
    @validator("subtitles")
    def validate_subtitles_order(cls, v):
        """Ensure subtitles are in chronological order."""
        for i in range(1, len(v)):
            if v[i].start_time < v[i - 1].start_time:
                raise ValueError("Subtitles must be in chronological order")
        return v


class BaseResponse(BaseModel):
    """Base response model."""

    success: bool
    error: Optional[str] = None


class FileInfo(BaseModel):
    """File information."""

    path: str
    name: str
    size: int = 0


class YouTubeDownloadResult(BaseResponse):
    """Result of YouTube video download operation."""

    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    metadata: Optional[VideoInfo] = None
    file_info: Optional[FileInfo] = None


class TranscriptExtractionResult(BaseResponse):
    """Result of transcript extraction operation."""

    transcript: List[TranscriptChunk] = Field(default_factory=list)
    language: str = ""
    total_segments: int = 0
    available_languages: List[str] = Field(default_factory=list)
    extraction_method: str = ""  # "youtube_api", "whisper", etc.


class ScenarioGenerationResult(BaseResponse):
    """Result of scenario generation operation."""

    scenarios: List[Scenario] = Field(default_factory=list)
    generation_info: Dict[str, Any] = Field(default_factory=dict)
    model_used: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0


class VideoProcessingResult(BaseResponse):
    """Result of video processing operation."""

    output_path: Optional[str] = None
    video_info: Dict[str, Any] = Field(default_factory=dict)
    segments_processed: int = 0
    processing_details: Dict[str, Any] = Field(default_factory=dict)


class CutSegmentValidationResult(BaseResponse):
    """Result of cut segment validation."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    total_duration: float = 0.0
    num_segments: int = 0
