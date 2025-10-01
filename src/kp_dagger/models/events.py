"""Event models for the event bus system."""

from __future__ import annotations

import uuid

# Import locally to avoid circular dependencies during model initialization
# Does not use dependency-injected timestamp service as Pydantic and DI don't play well
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, Field, field_validator

EventT = TypeVar("EventT", bound="BaseEvent")


class PathNormalizationMixin(BaseModel):
    """
    Mixin providing automatic Path-to-string normalization for resource_path fields.

    This allows event publishers to pass Path objects for convenience while
    ensuring event handlers always receive consistent string values.
    """

    resource_path: str | Path | None = Field(
        default=None,
        description="Canonical identifier for the resource (file path, URL, config hierarchy, etc.)",
    )
    display_name: str | None = Field(
        default=None,
        description="Optional user-friendly short name for UI display",
    )

    @field_validator("resource_path", mode="before")
    @classmethod
    def normalize_resource_path(cls, v: str | Path | None) -> str | None:
        """
        Convert Path objects to strings for consistent handler interface.

        Args:
            v: Input value (str, Path, or None)

        Returns:
            String representation of path, or None if input was None

        """
        if v is None:
            return None
        if isinstance(v, Path):
            return str(v)
        return v


class EventLevel(str, Enum):
    """Event severity levels for filtering and display purposes."""

    DEBUG = "debug"  # Detailed diagnostic information
    INFO = "info"  # General information about operations
    WARN = "warn"  # Warning conditions that don't prevent operation
    ERROR = "error"  # Error conditions that prevent or impair operation


__all__ = [
    "BaseEvent",
    "EventLevel",
    "EventT",
    "FindingDiscovered",
    "LogMessage",
    "MetricRecorded",
    "OperationCompleted",
    "OperationError",
    "OperationProgress",
    "OperationStarted",
    "all_event_types",
]


def _get_utc_now() -> datetime:
    """Get current UTC timestamp using centralized service approach."""
    return datetime.now(UTC)


class BaseEvent(BaseModel):
    """Base class for all events with automatic timestamp and correlation tracking."""

    # Does not inherit from KPDaggerBaseModel as that model is really built for business data
    # structures such as those that will end up in the database.  Instead, events are
    # transient in nature and should be as simple and serializable as possible.

    timestamp: datetime = Field(default_factory=_get_utc_now)
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    level: EventLevel = Field(
        default=EventLevel.INFO,
        description="Event severity level for filtering",
    )

    class Config:
        """Pydantic configuration."""

        # Allow Path objects and other complex types
        arbitrary_types_allowed = True
        # Use enum values for serialization
        use_enum_values = True


class OperationStarted(PathNormalizationMixin, BaseEvent):
    """Generic event for any operation beginning."""

    operation_type: str = Field(
        min_length=1,
        description="Type of operation (parsing, analysis, reporting)",
    )
    context: dict = Field(
        default_factory=dict,
        description="Operation-specific context",
    )
    batch_info: dict | None = Field(
        default=None,
        description="Batch processing information (current, total)",
    )


class OperationCompleted(PathNormalizationMixin, BaseEvent):
    """Generic event for any operation completion."""

    operation_type: str = Field(
        min_length=1,
        description="Type of operation that completed",
    )
    success: bool
    duration: float = Field(ge=0, description="Operation duration in seconds")
    results: dict = Field(
        default_factory=dict,
        description="Operation results and summary data",
    )


class OperationError(PathNormalizationMixin, BaseEvent):
    """Generic event for operation failures."""

    level: EventLevel = EventLevel.ERROR  # Always important
    operation_type: str = Field(
        min_length=1,
        description="Type of operation that failed",
    )
    error_message: str = Field(min_length=1, description="Error description")
    error_context: dict = Field(
        default_factory=dict,
        description="Additional error context",
    )


class OperationProgress(BaseEvent):
    """Generic event for operation progress updates."""

    operation_type: str = Field(
        min_length=1,
        description="Type of operation in progress",
    )
    progress_percent: float = Field(ge=0, le=100, description="Progress percentage")
    message: str = Field(min_length=1, description="Progress message")
    details: dict = Field(default_factory=dict, description="Progress-specific details")


class FindingDiscovered(BaseEvent):
    """Generic event for any type of finding (vuln, config, rules)."""

    finding_type: str = Field(
        min_length=1,
        description="Type of finding (vuln, config, rules)",
    )
    severity: str = Field(min_length=1, description="Finding severity level")
    identifier: str | None = Field(
        default=None,
        description="Finding identifier (CVE, rule ID, etc.)",
    )
    description: str = Field(min_length=1, description="Finding description")
    details: dict = Field(default_factory=dict, description="Finding-specific details")
    location: dict | None = Field(
        default=None,
        description="Location information (line number, section, etc.)",
    )


class LogMessage(BaseEvent):
    """Generic log message event for arbitrary logging needs."""

    message: str = Field(min_length=1, description="Log message")
    level: EventLevel = Field(default=EventLevel.INFO, description="Log level")
    logger_name: str = Field(
        default="DaggerScanner",
        description="Logger name/category",
    )
    extra: dict = Field(default_factory=dict, description="Extra log context")


class MetricRecorded(BaseEvent):
    """Event for recording metrics/measurements."""

    metric_name: str = Field(min_length=1)
    value: float = Field(description="Metric value")
    unit: str = Field(default="", description="Metric unit")
    tags: dict = Field(default_factory=dict, description="Metric tags")


# List of all event types for easy subscription
all_event_types: list[type[BaseEvent]] = [
    FindingDiscovered,
    LogMessage,
    MetricRecorded,
    OperationCompleted,
    OperationError,
    OperationProgress,
    OperationStarted,
]
