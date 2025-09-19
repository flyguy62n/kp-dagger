"""Event models for the event bus system."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, Field

EventT = TypeVar("EventT", bound="BaseEvent")


def _get_utc_now() -> datetime:
    """Get current UTC timestamp using centralized service approach."""
    # Import locally to avoid circular dependencies during model initialization
    # Does not use dependency-injected timestamp service as Pydantic and DI don't play well
    from datetime import UTC, datetime

    return datetime.now(UTC)


class BaseEvent(BaseModel):
    """Base class for all events with automatic timestamp and correlation tracking."""

    # Does not inherit from KPDaggerBaseModel as that model is really built for business data
    # structures such as those that will end up in the database.  Instead, events are
    # transient in nature and should be as simple and serializable as possible.

    timestamp: datetime = Field(default_factory=_get_utc_now)
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    class Config:
        """Pydantic configuration."""

        # Allow Path objects and other complex types
        arbitrary_types_allowed = True
        # Use enum values for serialization
        use_enum_values = True


class OperationStarted(BaseEvent):
    """Generic event for any operation beginning."""

    operation_type: str = Field(
        min_length=1,
        description="Type of operation (parsing, analysis, reporting)",
    )
    resource_path: Path | None = Field(
        default=None,
        description="Path to resource being processed",
    )
    context: dict = Field(
        default_factory=dict,
        description="Operation-specific context",
    )
    batch_info: dict | None = Field(
        default=None,
        description="Batch processing information (current, total)",
    )


class OperationCompleted(BaseEvent):
    """Generic event for any operation completion."""

    operation_type: str = Field(
        min_length=1,
        description="Type of operation that completed",
    )
    resource_path: Path | None = Field(
        default=None,
        description="Path to resource that was processed",
    )
    success: bool
    duration: float = Field(ge=0, description="Operation duration in seconds")
    results: dict = Field(
        default_factory=dict,
        description="Operation results and summary data",
    )


class OperationError(BaseEvent):
    """Generic event for operation failures."""

    operation_type: str = Field(
        min_length=1,
        description="Type of operation that failed",
    )
    resource_path: Path | None = Field(
        default=None,
        description="Path to resource being processed",
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
