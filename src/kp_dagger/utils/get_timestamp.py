"""
Timestamp utility functions for PyBastion.

This module provides utilities for generating timestamps in various formats,
commonly used for file naming, logging, and data serialization.

Functions:
    get_timestamp: Main timestamp function with configurable output formats
    get_formatted_timestamp: Get filename-friendly timestamp (YYYYMMDD-HHMMSS)
    get_iso_timestamp: Get ISO 8601 formatted timestamp
"""

from datetime import UTC, datetime

__all__: list[str] = [
    "get_formatted_timestamp",
    "get_iso_timestamp",
    "get_timestamp",
]


def get_timestamp(*, formatted: bool = False, iso: bool = False) -> datetime | str:
    """
    Generate a timestamp in various formats.

    Args:
        formatted: If True, return YYYYMMDD-HHMMSS format suitable for filenames
        iso: If True, return ISO 8601 format

    Returns:
        datetime object if no formatting specified, otherwise formatted string

    Examples:
        >>> get_timestamp()  # Returns datetime object
        >>> get_timestamp(formatted=True)  # Returns "20250629-143022"
        >>> get_timestamp(iso=True)  # Returns "2025-06-29T14:30:22.123456+00:00"

    """
    if formatted:
        return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    if iso:
        return datetime.now(UTC).isoformat()
    return datetime.now(UTC)


def get_formatted_timestamp() -> str:
    """Get a formatted timestamp string (YYYYMMDD-HHMMSS) suitable for filenames."""
    return get_timestamp(formatted=True)


def get_iso_timestamp() -> str:
    """Get an ISO 8601 formatted timestamp string."""
    return get_timestamp(iso=True)
