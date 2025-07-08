# -*- coding: utf-8 -*-
"""Base schemas for common patterns across the agent SDK."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response model for all API operations."""

    success: bool
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ProcessingResult(BaseResponse, Generic[T]):
    """Standard result wrapper for processing operations."""

    data: Optional[T] = None
    processing_info: Dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseResponse):
    """Result of validation operations."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response wrapper."""

    items: List[T] = Field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 50
    has_next: bool = False
    has_previous: bool = False


class ProcessingStatus(BaseModel):
    """Standard processing status tracking."""

    is_started: bool = False
    is_in_progress: bool = False
    is_completed: bool = False
    is_error: bool = False
    progress_percentage: float = 0.0
    current_step: str = ""
    total_steps: int = 0
    completed_steps: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class FileInfo(BaseModel):
    """File information model."""

    path: str
    name: str
    size: int = 0
    mime_type: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
