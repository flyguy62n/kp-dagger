"""
Rich output service for SSF Tools.

This module provides a Rich-based output service that implements the RichOutputProtocol
for dependency injection across the SSF Tools application.
"""

from kp_dagger.core.services.rich_output.protocols import (
    MessageSeverity,
    RichOutputProtocol,
)
from kp_dagger.core.services.rich_output.service import RichOutputService

__all__ = [
    "MessageSeverity",
    "RichOutputProtocol",
    "RichOutputService",
]
