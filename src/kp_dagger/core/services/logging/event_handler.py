"""
Logging event handler for capturing events to standard Python logging.

Provides structured logging of all system events while maintaining
separation from CLI display logic.
"""

import logging
from pathlib import Path

from kp_dagger.core.services.events.service import EventBusService
from kp_dagger.models.events import (
    FindingDiscovered,
    OperationCompleted,
    OperationError,
    OperationProgress,
    OperationStarted,
)


class LoggingEventHandler:
    """
    Event handler that captures events to Python logging system.

    Operates independently of CLI display - events are logged regardless
    of whether a CLI is present or not.
    """

    def __init__(
        self,
        event_bus: EventBusService,
        logger_name: str = "kp_dagger.events",
    ) -> None:
        self.logger = logging.getLogger(logger_name)
        self._setup_subscriptions(event_bus)

    def _setup_subscriptions(self, event_bus: EventBusService) -> None:
        """Subscribe to all event types for comprehensive logging."""
        event_bus.subscribe(OperationStarted, self.handle_operation_started)
        event_bus.subscribe(OperationCompleted, self.handle_operation_completed)
        event_bus.subscribe(OperationError, self.handle_operation_error)
        event_bus.subscribe(OperationProgress, self.handle_operation_progress)
        event_bus.subscribe(FindingDiscovered, self.handle_finding_discovered)

    def handle_operation_started(self, event: OperationStarted) -> None:
        """Log operation start with structured data."""
        extra_data = {
            "operation_type": event.operation_type,
            "resource_path": str(event.resource_path) if event.resource_path else None,
            "correlation_id": event.correlation_id,
            "context": event.context,
        }

        resource_name = (
            Path(str(event.resource_path)).name if event.resource_path else "N/A"
        )
        self.logger.info(
            "Operation started: %s on %s",
            event.operation_type,
            resource_name,
            extra=extra_data,
        )

    def handle_operation_completed(self, event: OperationCompleted) -> None:
        """Log operation completion with results and performance data."""
        extra_data = {
            "operation_type": event.operation_type,
            "resource_path": event.resource_path,
            "correlation_id": event.correlation_id,
            "success": event.success,
            "duration": event.duration,
            "results": event.results,
        }

        if event.success:
            # Specialized logging based on operation type
            if event.operation_type == "device_metadata_extraction":
                self.logger.info(
                    "Device identified: %s running %s",
                    event.results.get("hardware", "unknown"),
                    event.results.get("sw_version", "unknown"),
                    extra=extra_data,
                )
            elif event.operation_type == "parsing":
                sections_count = event.results.get("sections_count", 0)
                self.logger.info(
                    "Configuration parsed: %d sections in %.2fs",
                    sections_count,
                    event.duration,
                    extra=extra_data,
                )
            else:
                self.logger.info(
                    "Operation completed: %s (%.2fs)",
                    event.operation_type,
                    event.duration,
                    extra=extra_data,
                )
        else:
            self.logger.warning(
                "Operation completed with issues: %s",
                event.operation_type,
                extra=extra_data,
            )

    def handle_operation_error(self, event: OperationError) -> None:
        """Log operation errors with full context."""
        if event.error_message.startswith("Unrecognized line format"):
            return  # Suppress known non-critical parsing errors

        extra_data = {
            "operation_type": event.operation_type,
            "resource_path": event.resource_path,
            "correlation_id": event.correlation_id,
            "error_context": event.error_context,
        }

        self.logger.error(
            "Operation failed: %s - %s",
            event.operation_type,
            event.error_message,
            extra=extra_data,
        )

    def handle_operation_progress(self, event: OperationProgress) -> None:
        """Log progress updates at debug level to avoid spam."""
        extra_data = {
            "operation_type": event.operation_type,
            "progress_percent": event.progress_percent,
            "correlation_id": event.correlation_id,
            "details": event.details,
        }

        self.logger.debug(
            "Progress: %s %.1f%% - %s",
            event.operation_type,
            event.progress_percent,
            event.message,
            extra=extra_data,
        )

    def handle_finding_discovered(self, event: FindingDiscovered) -> None:
        """Log security/compliance findings with full details."""
        extra_data = {
            "finding_type": event.finding_type,
            "severity": event.severity,
            "identifier": event.identifier,
            "correlation_id": event.correlation_id,
            "details": event.details,
            "location": event.location,
        }

        # Use appropriate log level based on finding severity
        log_level = self._map_severity_to_log_level(event.severity)

        self.logger.log(
            log_level,
            "Finding discovered: %s [%s] %s",
            event.identifier or "N/A",
            event.severity.upper(),
            event.description,
            extra=extra_data,
        )

    def _map_severity_to_log_level(self, severity: str) -> int:
        """Map finding severity to Python logging levels."""
        severity_map = {
            "critical": logging.CRITICAL,
            "high": logging.ERROR,
            "medium": logging.WARNING,
            "low": logging.INFO,
            "info": logging.INFO,
        }
        return severity_map.get(severity.lower(), logging.INFO)
