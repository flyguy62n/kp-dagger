"""Path utilities for file processing in the KP Analysis Toolkit."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kp_dagger.core.services.timestamp.protocols import TimestampProtocol
    from kp_dagger.models.base.types import PathLike


class PathUtilitiesService:
    """Service for generating paths with timestamps."""

    def __init__(self, timestamp_service: TimestampProtocol) -> None:
        """
        Initialize the PathUtilitiesService.

        Args:
            timestamp_service: Service for generating timestamps

        """
        self.timestamp_service: TimestampProtocol = timestamp_service

    def generate_timestamped_path(
        self,
        base_path: PathLike,
        filename_prefix: str,
        extension: str,
    ) -> Path:
        """Generate a timestamped file path."""
        timestamp: str = self.timestamp_service.format_filename_now()

        return Path(base_path) / f"{filename_prefix}_{timestamp}{extension}"
