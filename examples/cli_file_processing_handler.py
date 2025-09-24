"""Example CLI event handler for file processing events."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kp_dagger.core.services.rich_output.protocols import RichOutputProtocol
    from kp_dagger.models.events import (
        OperationCompleted,
        OperationError,
        OperationStarted,
    )


class FileProcessingCliEventHandler:
    """CLI event handler for file processing operations."""

    def __init__(self, rich_output: RichOutputProtocol) -> None:
        """
        Initialize the CLI event handler.

        Args:
            rich_output: Rich output service for console display

        """
        self.rich_output = rich_output

    def handle_operation_started(self, event: OperationStarted) -> None:
        """
        Handle file processing operation start events.

        Args:
            event: The operation started event

        """
        if event.operation_type == "file_processing":
            operation = event.context.get("operation", "processing")
            resource_name = (
                event.resource_path.name if event.resource_path else "unknown"
            )
            self.rich_output.info(f"Starting {operation} for {resource_name}...")

        elif event.operation_type == "file_discovery":
            pattern = event.context.get("pattern", "*")
            recursive = event.context.get("recursive", False)
            mode = "recursively" if recursive else "in directory"
            resource_name = (
                event.resource_path.name if event.resource_path else "unknown"
            )
            self.rich_output.info(
                f"Searching {mode} {resource_name} for pattern '{pattern}'...",
            )

    def handle_operation_completed(self, event: OperationCompleted) -> None:
        """
        Handle file processing operation completion events.

        Args:
            event: The operation completed event

        """
        if event.operation_type == "file_processing" and event.success:
            results = event.results
            resource_name = (
                event.resource_path.name if event.resource_path else "unknown"
            )
            encoding = results.get("encoding", "unknown")
            mime_type = results.get("mime_type", "unknown")
            is_text = results.get("is_text", False)
            file_type = "text" if is_text else "binary"

            self.rich_output.success(
                f"✓ {resource_name} processed successfully "
                f"({file_type}, {encoding}, {mime_type}, {event.duration:.2f}s)",
            )

        elif event.operation_type == "file_discovery" and event.success:
            results = event.results
            files_found = results.get("files_found", 0)
            pattern = results.get("pattern", "*")

            if files_found > 0:
                self.rich_output.success(
                    f"✓ Found {files_found} files matching '{pattern}' ({event.duration:.2f}s)",
                )
            else:
                self.rich_output.warning(
                    f"⚠ No files found matching '{pattern}' ({event.duration:.2f}s)",
                )

        elif not event.success:
            self.rich_output.warning(f"⚠ {event.operation_type} completed with issues")

    def handle_operation_error(self, event: OperationError) -> None:
        """
        Handle file processing operation error events.

        Args:
            event: The operation error event

        """
        resource_name = event.resource_path.name if event.resource_path else "unknown"
        operation = event.error_context.get("operation", event.operation_type)

        if event.operation_type == "file_processing":
            if operation == "file_validation":
                self.rich_output.error(f"✗ File not found: {resource_name}")
            elif operation == "encoding_detection":
                self.rich_output.error(
                    f"✗ Could not detect encoding for: {resource_name}",
                )
            else:
                self.rich_output.error(
                    f"✗ Failed to process {resource_name}: {event.error_message}",
                )

        elif event.operation_type == "file_discovery":
            pattern = event.error_context.get("pattern", "*")
            self.rich_output.error(
                f"✗ Failed to search for '{pattern}' in {resource_name}: {event.error_message}",
            )

        else:
            self.rich_output.error(
                f"✗ {event.operation_type} failed: {event.error_message}",
            )
