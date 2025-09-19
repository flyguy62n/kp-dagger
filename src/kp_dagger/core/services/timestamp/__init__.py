"""Timestamp service package."""

from kp_dagger.core.services.timestamp.protocols import TimestampProtocol
from kp_dagger.core.services.timestamp.service import TimestampService

__all__ = ["TimestampProtocol", "TimestampService"]
