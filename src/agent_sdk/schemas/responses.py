# -*- coding: utf-8 -*-
"""Standard response wrappers for tool and API operations."""

from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel, Field
from .base import BaseResponse

T = TypeVar("T")


class ApiResponse(BaseResponse, Generic[T]):
    """Generic API response wrapper."""

    data: Optional[T] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolResponse(BaseResponse, Generic[T]):
    """Standard response format for function tools."""

    result: Optional[T] = None
    execution_info: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def success(cls, result: T, **execution_info) -> "ToolResponse[T]":
        """Create a successful response."""
        return cls(success=True, result=result, execution_info=execution_info)

    @classmethod
    def error(cls, error_message: str, **execution_info) -> "ToolResponse[T]":
        """Create an error response."""
        return cls(success=False, error=error_message, execution_info=execution_info)


class BatchResponse(BaseResponse, Generic[T]):
    """Response for batch operations."""

    results: list[T] = Field(default_factory=list)
    successful_count: int = 0
    failed_count: int = 0
    total_count: int = 0

    def add_result(self, result: T, is_success: bool = True):
        """Add a result to the batch."""
        self.results.append(result)
        self.total_count += 1
        if is_success:
            self.successful_count += 1
        else:
            self.failed_count += 1
