# Event Bus Pattern

The Event Bus Pattern provides a publish-subscribe mechanism that enables complete decoupling between services and user interfaces.

## Architecture

The `EventBusService` provides a pub-sub pattern where services publish events without knowing who (if anyone) is listening.

## Event Types

Events are strongly typed using Pydantic models for consistency with the project's data validation patterns:

```python
# models/events.py
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
from datetime import datetime
from typing import Literal
import uuid

class BaseEvent(BaseModel):
    """Base class for all events with automatic timestamp and correlation tracking."""
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    class Config:
        # Allow Path objects and other complex types
        arbitrary_types_allowed = True
        # Use enum values for serialization
        use_enum_values = True

# Generic event types that balance flexibility with type safety

class OperationStarted(BaseEvent):
    """Generic event for any operation beginning."""
    operation_type: str = Field(min_length=1, description="Type of operation (parsing, analysis, reporting)")
    resource_path: Path | None = Field(default=None, description="Path to resource being processed")
    context: dict = Field(default_factory=dict, description="Operation-specific context")
    batch_info: dict | None = Field(default=None, description="Batch processing information (current, total)")

class OperationCompleted(BaseEvent):
    """Generic event for any operation completion."""
    operation_type: str = Field(min_length=1, description="Type of operation that completed")
    resource_path: Path | None = Field(default=None, description="Path to resource that was processed")
    success: bool
    duration: float = Field(ge=0, description="Operation duration in seconds")
    results: dict = Field(default_factory=dict, description="Operation results and summary data")

class OperationError(BaseEvent):
    """Generic event for operation failures."""
    operation_type: str = Field(min_length=1, description="Type of operation that failed")
    resource_path: Path | None = Field(default=None, description="Path to resource being processed")
    error_message: str = Field(min_length=1, description="Error description")
    error_context: dict = Field(default_factory=dict, description="Additional error context")

class OperationProgress(BaseEvent):
    """Generic event for operation progress updates."""
    operation_type: str = Field(min_length=1, description="Type of operation in progress")
    progress_percent: float = Field(ge=0, le=100, description="Progress percentage")
    message: str = Field(min_length=1, description="Progress message")
    details: dict = Field(default_factory=dict, description="Progress-specific details")

class FindingDiscovered(BaseEvent):
    """Generic event for any type of finding (vuln, config, rules)."""
    finding_type: str = Field(min_length=1, description="Type of finding (vuln, config, rules)")
    severity: str = Field(min_length=1, description="Finding severity level")
    identifier: str | None = Field(default=None, description="Finding identifier (CVE, rule ID, etc.)")
    description: str = Field(min_length=1, description="Finding description")
    details: dict = Field(default_factory=dict, description="Finding-specific details")
    location: dict | None = Field(default=None, description="Location information (line number, section, etc.)")
```

## Service Implementation

Services publish events without any knowledge of UI implementations and can function independently of event systems:

```python
# services/parsing/service.py
from typing import Protocol

class IEventPublisher(Protocol):
    """Optional event publishing interface for UI decoupling."""
    def publish(self, event: BaseEvent) -> None: ...

class NullEventPublisher:
    """No-op implementation for services that don't need events."""
    def publish(self, event: BaseEvent) -> None:
        pass  # Do nothing - service works without UI

class SafeEventPublisher:
    """Wrapper that makes event publishing safe and eliminates boilerplate."""
    
    def __init__(self, publisher: IEventPublisher | None = None, logger: LoggingService | None = None):
        self.publisher = publisher or NullEventPublisher()
        self.logger = logger

    def publish(self, event: BaseEvent) -> None:
        """Safely publish events with automatic error handling."""
        try:
            self.publisher.publish(event)
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Event publishing failed: {e}")
            # Never let event publishing break business logic
            pass

class ParsingService:
    @inject
    def __init__(
        self,
        event_publisher: SafeEventPublisher = Provide[CoreContainer.safe_event_publisher],
        file_handler: FileHandlingService = Provide[CoreContainer.file_handling_service],
        logger: LoggingService = Provide[CoreContainer.logging_service],
    ):
        self.event_publisher = event_publisher  # Already safe - no boilerplate needed
        self.file_handler = file_handler
        self.logger = logger

    def parse_file(self, file_path: Path, vendor_type: str) -> ParseResult:
        # Clean, direct event publishing with generic event types
        self.event_publisher.publish(OperationStarted(
            operation_type="parsing",
            resource_path=file_path,
            context={"vendor_type": vendor_type}
        ))
        
        try:
            # Perform parsing logic
            content = self.file_handler.read_file(file_path)
            
            # Validate syntax
            if not self._validate_syntax(content, vendor_type):
                raise ParseError(f"Invalid {vendor_type} configuration syntax")
            
            # Parse content
            result = self._parse_content(content, vendor_type)
            
            # Clean event publishing with results
            self.event_publisher.publish(OperationCompleted(
                operation_type="parsing",
                resource_path=file_path,
                success=True,
                duration=1.2,
                results={"rules_count": len(result.rules), "vendor_type": vendor_type}
            ))
            
            return result
            
        except Exception as e:
            # Clean error event publishing
            self.event_publisher.publish(OperationError(
                operation_type="parsing",
                resource_path=file_path,
                error_message=str(e),
                error_context={"vendor_type": vendor_type}
            ))
            
            # Log error (separate from event publishing)
            self.logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def parse_multiple_files(self, file_paths: list[Path]) -> list[ParseResult]:
        results = []
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths, 1):
            vendor_type = self._detect_vendor_type(file_path)
            
            # Clean event publishing with batch context
            self.event_publisher.publish(OperationStarted(
                operation_type="parsing",
                resource_path=file_path,
                context={"vendor_type": vendor_type},
                batch_info={"current": i, "total": total_files}
            ))
            
            try:
                result = self._parse_single_file(file_path, vendor_type)
                results.append(result)
            except Exception as e:
                # Continue processing other files
                self.logger.warning(f"Skipping {file_path} due to error: {e}")
                continue
        
        return results
```

## UI Event Handlers

Each UI implementation creates its own event handlers:

### CLI Event Handler

```python
# cli/events/handlers.py
class CliEventHandler:
    def __init__(self, rich_output: RichOutputService):
        self.rich_output = rich_output
        self.current_progress = None
        self.file_progress = None

    def handle_operation_started(self, event: OperationStarted) -> None:
        """Handle any operation start with context-aware messaging."""
        if event.operation_type == "parsing":
            vendor_type = event.context.get("vendor_type", "unknown")
            batch_info = event.batch_info
            if batch_info:
                self.rich_output.info(
                    f"[{batch_info['current']}/{batch_info['total']}] "
                    f"[{vendor_type}] Processing {event.resource_path.name}..."
                )
            else:
                self.rich_output.info(
                    f"[{vendor_type}] Processing {event.resource_path.name}..."
                )
        elif event.operation_type == "analysis":
            analysis_type = event.context.get("analysis_type", "unknown")
            self.rich_output.info(f"Starting {analysis_type} analysis...")

    def handle_operation_completed(self, event: OperationCompleted) -> None:
        """Handle any operation completion with result-aware messaging."""
        if event.operation_type == "parsing" and event.success:
            results = event.results
            self.rich_output.success(
                f"✓ {event.resource_path.name} parsed successfully "
                f"({results.get('rules_count', 0)} rules found, {event.duration:.1f}s)"
            )
        elif event.operation_type == "analysis" and event.success:
            results = event.results
            findings = results.get("findings_count", 0)
            self.rich_output.success(f"✓ Analysis completed ({findings} findings, {event.duration:.1f}s)")
        elif not event.success:
            self.rich_output.warning(f"⚠ {event.operation_type} completed with issues")

    def handle_operation_error(self, event: OperationError) -> None:
        """Handle any operation error with context-aware messaging."""
        context_info = ""
        if event.operation_type == "parsing" and "line_number" in event.error_context:
            context_info = f" at line {event.error_context['line_number']}"
        
        resource_name = event.resource_path.name if event.resource_path else "unknown"
        self.rich_output.error(
            f"✗ Failed {event.operation_type} on {resource_name}{context_info}: {event.error_message}"
        )

    def handle_finding_discovered(self, event: FindingDiscovered) -> None:
        """Handle any type of finding with type-aware formatting."""
        if event.finding_type == "vuln":
            severity_color = {
                "critical": "red",
                "high": "orange", 
                "medium": "yellow",
                "low": "blue"
            }.get(event.severity.lower(), "white")
            
            identifier = event.identifier or "N/A"
            self.rich_output.warning(
                f"🔒 [{severity_color}]{event.severity.upper()}[/] "
                f"{identifier}: {event.description}"
            )
        
        elif event.finding_type == "config":
            location_info = ""
            if event.location and "line_number" in event.location:
                location_info = f" (line {event.location['line_number']})"
            
            rule_id = event.identifier or "Unknown Rule"
            recommendation = event.details.get("recommendation", "No recommendation available")
            self.rich_output.warning(
                f"📋 CIS {rule_id}: {event.description}{location_info}\n"
                f"   💡 {recommendation}"
            )
        
        elif event.finding_type == "rules":
            self.rich_output.warning(
                f"🚫 Rule {event.severity.upper()}: {event.description}"
            )
```

### GUI Event Handler (Future)

```python
# gui/events/handlers.py
class GuiEventHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.progress_dialog = None

    def handle_operation_started(self, event: OperationStarted) -> None:
        """Handle any operation start with GUI progress updates."""
        if event.operation_type == "parsing" and event.batch_info:
            if not self.progress_dialog:
                self.progress_dialog = QProgressDialog(
                    "Processing files...", 
                    "Cancel", 
                    0, 
                    event.batch_info["total"],
                    self.main_window
                )
            
            self.progress_dialog.setValue(event.batch_info["current"] - 1)
            self.progress_dialog.setLabelText(f"Processing {event.resource_path.name}")

    def handle_finding_discovered(self, event: FindingDiscovered) -> None:
        """Handle any finding with type-aware GUI notifications."""
        if event.finding_type == "vuln" and event.severity in ["critical", "high"]:
            QMessageBox.warning(
                self.main_window,
                f"{event.severity.title()} Vulnerability",
                f"{event.identifier}: {event.description}"
            )
        elif event.finding_type == "config":
            # Could add to compliance violations list widget
            self.main_window.add_compliance_violation(event)
        elif event.finding_type == "rules":
            # Could add to firewall rules review list widget
            self.main_window.add_rule_violation(event)
```

## Event Subscription

UIs subscribe to events they care about:

```python
# cli/commands/scan.py
@click.command()
@inject
def scan(
    config_paths: list[str],
    event_bus: EventBusService = Provide[CoreContainer.event_bus_service],
    workflow: WorkflowService = Provide[CoreContainer.workflow_service],
    rich_output: RichOutputService = Provide[CoreContainer.rich_output_service],
):
    # Create CLI event handler
    cli_handler = CliEventHandler(rich_output)
    
    # Subscribe to generic events with flexible handling
    event_bus.subscribe(OperationStarted, cli_handler.handle_operation_started)
    event_bus.subscribe(OperationCompleted, cli_handler.handle_operation_completed)
    event_bus.subscribe(OperationError, cli_handler.handle_operation_error)
    event_bus.subscribe(FindingDiscovered, cli_handler.handle_finding_discovered)
    
    # Execute workflow - services will publish events
    try:
        results = workflow.scan_configurations([Path(p) for p in config_paths])
        
        # Final summary (CLI-specific logic)
        total_files = len(config_paths)
        successful = sum(1 for r in results if r.success)
        rich_output.info(f"\nScan completed: {successful}/{total_files} files processed successfully")
        
    except KeyboardInterrupt:
        rich_output.warning("Scan cancelled by user")
    except Exception as e:
        rich_output.error(f"Scan failed: {e}")
        raise click.ClickException(str(e))
```

## Dependency Injection Configuration

The safe event publisher is configured through dependency injection to eliminate boilerplate:

```python
# containers/core.py
class CoreContainer(DeclarativeContainer):
    # Core logging service
    logging_service = providers.Singleton(LoggingService)
    
    # Core event bus service with memory management
    event_bus_service = providers.Singleton(
        EventBusService,
        logger=logging_service
    )
    
    # Safe event publisher wrapper - eliminates boilerplate in services
    safe_event_publisher = providers.Factory(
        SafeEventPublisher,
        publisher=event_bus_service,  # EventBusService implements IEventPublisher
        logger=logging_service
    )
    
    # Services automatically get the safe wrapper
    parsing_service = providers.Factory(
        ParsingService,
        event_publisher=safe_event_publisher,  # No boilerplate needed in service
        file_handler=file_handling_service,
        logger=logging_service,
    )
    
    analysis_service = providers.Factory(
        AnalysisService,
        event_publisher=safe_event_publisher,  # Same safe wrapper for all services
        vulnerability_analyzer=vulnerability_analyzer,
        compliance_analyzer=compliance_analyzer,
        logger=logging_service,
    )
```

## Benefits

- **Decoupled Architecture**: Services and UIs are completely independent
- **Type Safety**: Strongly typed events prevent runtime errors
- **Fail-Safe Design**: Event publishing failures never break business logic
- **Flexible Handling**: UIs can choose which events to handle and how
- **Easy Testing**: Business logic can be tested without mocking event systems

## Next Steps

- [Memory Management](memory-management.md) - Learn about automatic subscription cleanup
- [Progress Callbacks](progress-callbacks.md) - Implement fine-grained progress reporting
