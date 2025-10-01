"""
CLI Event Handler for Rich terminal display.

Provides context-aware event handling that displays appropriate
messages and formatting for terminal user interfaces.
"""

from kp_dagger.cli.utils.output import RichOutputService
from kp_dagger.core.services.events.service import EventBusService
from kp_dagger.models.events import (
    FindingDiscovered,
    OperationCompleted,
    OperationError,
    OperationProgress,
    OperationStarted,
)


class CLIEventHandler:
    """
    Central event handler for CLI display using Rich output.

    Routes events to appropriate display handlers based on operation type
    and context. Operates independently of logging - events are displayed
    AND logged via separate handlers.
    """

    def __init__(
        self,
        rich_output: RichOutputService,
        event_bus: EventBusService,
    ) -> None:
        self.rich_output = rich_output
        self._setup_subscriptions(event_bus)

    def _setup_subscriptions(self, event_bus: EventBusService) -> None:
        """Subscribe to all relevant event types for CLI display."""
        event_bus.subscribe(OperationStarted, self.handle_operation_started)
        event_bus.subscribe(OperationCompleted, self.handle_operation_completed)
        event_bus.subscribe(OperationError, self.handle_operation_error)
        event_bus.subscribe(OperationProgress, self.handle_operation_progress)
        event_bus.subscribe(FindingDiscovered, self.handle_finding_discovered)

    def handle_operation_started(self, event: OperationStarted) -> None:
        """Handle operation start with context-aware messaging."""
        if event.operation_type == "parsing":
            # Skip internal parsing events without a resource identifier
            if not event.resource_path and not event.display_name:
                return

            device_type = event.context.get("device_type", "unknown")
            batch_info = event.batch_info
            resource_name = event.display_name or event.resource_path or "N/A"
            if batch_info:
                self.rich_output.info(
                    f"[{batch_info['current']}/{batch_info['total']}] "
                    f"[{device_type}] Processing {resource_name}...",
                )
            else:
                self.rich_output.info(f"[{device_type}] Processing {resource_name}...")
        elif event.operation_type == "analysis":
            analysis_type = event.context.get("analysis_type", "security")
            self.rich_output.info(f"🔍 Starting {analysis_type} analysis...")

    def handle_operation_completed(self, event: OperationCompleted) -> None:
        """Handle operation completion with result-aware messaging."""
        if event.operation_type == "device_metadata_extraction" and event.success:
            # Device identification display
            hardware = event.results.get("hardware", "Unknown")
            sw_version = event.results.get("sw_version", "Unknown")
            self.rich_output.info(
                f"📟 Device identified: {hardware} running {sw_version}",
            )

        elif event.operation_type == "parsing" and event.success:
            # Parsing success with section count
            results = event.results
            resource_name = event.display_name or event.resource_path or "N/A"
            sections_count = results.get("sections_count", 0)
            self.rich_output.success(
                f"✅ Parsed {resource_name} - {sections_count} sections",
            )

        elif event.operation_type == "analysis" and event.success:
            # Analysis completion with findings summary
            results = event.results
            findings = results.get("findings_count", 0)
            duration = event.duration
            self.rich_output.success(
                f"✅ Analysis completed - {findings} findings ({duration:.1f}s)",
            )

        elif not event.success:
            # Generic failure message
            self.rich_output.warning(f"⚠️  {event.operation_type} completed with issues")

    def handle_operation_error(self, event: OperationError) -> None:
        """Handle operation errors with context-aware messaging."""
        if event.error_message.startswith("Unrecognized line format"):
            return  # Suppress known non-critical parsing errors

        context_info = ""
        if "line_number" in event.error_context:
            context_info = f" at line {event.error_context['line_number']}"

        resource_name = (
            event.display_name or event.resource_path or "unknown resource"
        )
        self.rich_output.error(
            f"❌ Failed {event.operation_type} on {resource_name}{context_info}: {event.error_message}",
        )

    def handle_operation_progress(self, event: OperationProgress) -> None:
        """Handle progress updates (typically used by Progress bars, not direct display)."""
        # Progress events are usually handled by Rich Progress bars
        # This is here for completeness but may not display directly
        _ = event  # Suppress unused argument warning

    def handle_finding_discovered(self, event: FindingDiscovered) -> None:
        """Handle security/compliance findings with severity-based formatting."""
        severity_icons = {
            "critical": "🚨",
            "high": "🔴",
            "medium": "🟡",
            "low": "🔵",
            "info": "💡",
        }

        severity_colors = {
            "critical": "bold red",
            "high": "red",
            "medium": "yellow",
            "low": "blue",
            "info": "cyan",
        }

        icon = severity_icons.get(event.severity.lower(), "🔍")
        color = severity_colors.get(event.severity.lower(), "white")

        identifier_text = f" [{event.identifier}]" if event.identifier else ""

        # Use appropriate Rich method based on severity
        if event.severity.lower() in ["critical", "high"]:
            self.rich_output.error(
                f"{icon} [{color}]{event.finding_type.upper()}{identifier_text}[/{color}]: {event.description}",
            )
        elif event.severity.lower() == "medium":
            self.rich_output.warning(
                f"{icon} [{color}]{event.finding_type.upper()}{identifier_text}[/{color}]: {event.description}",
            )
        else:
            self.rich_output.info(
                f"{icon} [{color}]{event.finding_type.upper()}{identifier_text}[/{color}]: {event.description}",
            )
