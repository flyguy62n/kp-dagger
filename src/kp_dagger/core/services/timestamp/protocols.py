"""Timestamp service interfaces for dependency injection."""

from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class TimestampProtocol(Protocol):
    """Protocol defining the timestamp service interface for dependency injection."""

    def now(self) -> datetime:
        """Get current local datetime."""
        ...

    def utc_now(self) -> datetime:
        """Get current UTC datetime."""
        ...

    def format_iso(self, dt: datetime) -> str:
        """Format datetime as ISO 8601 string."""
        ...

    def format_rfc3339(self, dt: datetime) -> str:
        """Format datetime as RFC 3339 string."""
        ...

    def format_filename(self, dt: datetime) -> str:
        """Format datetime for use in filenames (YYYYMMDD-HHMMSS)."""
        ...

    def format_filename_now(self) -> str:
        """Format current local time for use in filenames (YYYYMMDD-HHMMSS)."""
        ...

    def reset_filename_cache(self) -> None:
        """Reset the cached filename timestamp to force regeneration on next call."""
        ...

    def parse_iso(self, iso_string: str) -> datetime:
        """Parse ISO 8601 string to datetime."""
        ...

    def to_utc(self, dt: datetime) -> datetime:
        """Convert datetime to UTC."""
        ...

    def from_timestamp(self, timestamp: float) -> datetime:
        """Create datetime from Unix timestamp."""
        ...

    def to_timestamp(self, dt: datetime) -> float:
        """Convert datetime to Unix timestamp."""
        ...

    def elapsed_seconds(
        self,
        start_time: datetime,
        end_time: datetime | None = None,
    ) -> float:
        """Calculate elapsed seconds between two datetimes."""
        ...

    def add_seconds(self, dt: datetime, seconds: float) -> datetime:
        """Add seconds to a datetime."""
        ...
