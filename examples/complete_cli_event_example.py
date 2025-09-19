"""Complete CLI example showing event bus subscription and usage."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kp_dagger.core.services.events import EventBusService
    from kp_dagger.core.services.file_processing.service import FileProcessingService
    from kp_dagger.core.services.rich_output.interfaces import RichOutputProtocol

from cli_file_processing_handler import FileProcessingCliEventHandler

from kp_dagger.models.events import OperationCompleted, OperationError, OperationStarted


def run_file_processing_example(
    file_paths: list[str],
    event_bus: EventBusService,
    file_processing_service: FileProcessingService,
    rich_output: RichOutputProtocol,
) -> None:
    """
    Complete example showing how CLI subscribes to events.

    Args:
        file_paths: List of file paths to process
        event_bus: The event bus service for pub-sub
        file_processing_service: Service that will publish events
        rich_output: Rich output service for console display

    """
    # 1. Create the CLI event handler
    cli_handler = FileProcessingCliEventHandler(rich_output)

    # 2. Subscribe to events - THIS IS WHAT YOU WERE LOOKING FOR!
    event_bus.subscribe(OperationStarted, cli_handler.handle_operation_started)
    event_bus.subscribe(OperationCompleted, cli_handler.handle_operation_completed)
    event_bus.subscribe(OperationError, cli_handler.handle_operation_error)

    # 3. Execute the service operations (services will publish events)
    try:
        results = []
        for file_path in file_paths:
            path = Path(file_path)
            # This will trigger OperationStarted, OperationCompleted/OperationError events
            result = file_processing_service.process_file(path)
            results.append(result)

        # 4. CLI-specific summary logic
        successful = sum(1 for r in results if r.success)
        total = len(results)
        rich_output.info(
            f"\nProcessing completed: {successful}/{total} files processed successfully",
        )

    finally:
        # 5. Clean up subscriptions (optional in short-lived CLI)
        event_bus.unsubscribe(OperationStarted, cli_handler.handle_operation_started)
        event_bus.unsubscribe(
            OperationCompleted,
            cli_handler.handle_operation_completed,
        )
        event_bus.unsubscribe(OperationError, cli_handler.handle_operation_error)


def run_file_discovery_example(
    directory_path: str,
    pattern: str,
    event_bus: EventBusService,
    file_processing_service: FileProcessingService,
    rich_output: RichOutputProtocol,
) -> None:
    """
    Example showing file discovery with event bus.

    Args:
        directory_path: Directory to search in
        pattern: File pattern to search for
        event_bus: The event bus service
        file_processing_service: Service that will publish events
        rich_output: Rich output service for console display

    """
    # Create handler and subscribe to events
    cli_handler = FileProcessingCliEventHandler(rich_output)
    event_bus.subscribe(OperationStarted, cli_handler.handle_operation_started)
    event_bus.subscribe(OperationCompleted, cli_handler.handle_operation_completed)
    event_bus.subscribe(OperationError, cli_handler.handle_operation_error)

    try:
        # This will trigger events for the discovery operation
        files = file_processing_service.discover_files_by_pattern(
            base_path=Path(directory_path),
            pattern=pattern,
            recursive=True,
        )

        # Process each found file
        if files:
            rich_output.info(f"Processing {len(files)} discovered files...")
            for file_path in files:
                file_processing_service.process_file(file_path)
        else:
            rich_output.warning("No files found to process")

    finally:
        # Clean up subscriptions
        event_bus.unsubscribe(OperationStarted, cli_handler.handle_operation_started)
        event_bus.unsubscribe(
            OperationCompleted,
            cli_handler.handle_operation_completed,
        )
        event_bus.unsubscribe(OperationError, cli_handler.handle_operation_error)


# Example usage with dependency injection (how it would be called)
def example_with_di() -> None:
    """
    Example showing how this would be used with dependency injection.

    This would typically be in a Click command or main() function.
    """
    # These would come from DI container in real usage
    # from kp_dagger.core.services.events import EventBusService
    # from kp_dagger.core.services.file_processing.service import FileProcessingService
    # ... other imports

    # Create services (normally injected)
    # event_bus = EventBusService()
    # file_processing_service = FileProcessingService(event_publisher=SafeEventPublisher(event_bus), ...)
    # rich_output = RichOutputService()

    # Run the example
    # file_paths = ["config1.txt", "config2.txt"]
    # run_file_processing_example(file_paths, event_bus, file_processing_service, rich_output)


def create_mock_services() -> tuple:
    """Create mock services for demonstration purposes."""
    from datetime import datetime

    from kp_dagger.core.services.events import EventBusService, SafeEventPublisher

    # Mock timestamp service
    class MockTimestampService:
        def get_current_timestamp(self) -> datetime:
            return datetime.now()

    # Mock rich output service
    class MockRichOutput:
        def info(self, message: str) -> None:
            print(f"ℹ️  {message}")

        def success(self, message: str) -> None:
            print(f"✅ {message}")

        def warning(self, message: str) -> None:
            print(f"⚠️  {message}")

        def error(self, message: str) -> None:
            print(f"❌ {message}")

    # Mock file processing service
    class MockFileProcessingService:
        def __init__(self, event_publisher, timestamp_service):
            self.event_publisher = event_publisher
            self.timestamp_service = timestamp_service

        def discover_files_by_pattern(
            self,
            base_path: Path,
            pattern: str,
            recursive: bool = True,
        ) -> list[Path]:
            from kp_dagger.models.events import OperationCompleted, OperationStarted

            # Publish start event
            self.event_publisher.publish(
                OperationStarted(
                    operation_type="file_discovery",
                    resource_path=base_path,
                    context={"pattern": pattern, "recursive": recursive},
                ),
            )

            # Mock discovery logic - find some example files
            files = []
            if base_path.exists():
                if recursive:
                    files = list(base_path.rglob(pattern))
                else:
                    files = list(base_path.glob(pattern))

            # Publish completion event
            self.event_publisher.publish(
                OperationCompleted(
                    operation_type="file_discovery",
                    resource_path=base_path,
                    success=True,
                    duration=0.1,
                    results={"files_found": len(files), "pattern": pattern},
                ),
            )

            return files

        def process_file(self, file_path: Path):
            from kp_dagger.models.events import OperationCompleted, OperationStarted

            # Publish start event
            self.event_publisher.publish(
                OperationStarted(
                    operation_type="file_processing",
                    resource_path=file_path,
                    context={"operation": "processing"},
                ),
            )

            # Mock processing
            import time

            time.sleep(0.05)  # Simulate work

            # Publish completion event
            self.event_publisher.publish(
                OperationCompleted(
                    operation_type="file_processing",
                    resource_path=file_path,
                    success=True,
                    duration=0.05,
                    results={
                        "encoding": "utf-8",
                        "mime_type": "text/plain",
                        "is_text": True,
                    },
                ),
            )

    # Create services
    event_bus = EventBusService()
    timestamp_service = MockTimestampService()
    safe_publisher = SafeEventPublisher(event_bus)
    file_service = MockFileProcessingService(safe_publisher, timestamp_service)
    rich_output = MockRichOutput()

    return event_bus, file_service, rich_output


if __name__ == "__main__":
    print("🚀 Running CLI Event Bus Discovery Example\n")

    # Create mock services
    event_bus, file_processing_service, rich_output = create_mock_services()

    # Run the discovery example on the current directory
    current_dir = Path.cwd()
    pattern = "*.py"

    print(f"📁 Searching for '{pattern}' files in: {current_dir}")
    print("=" * 60)

    run_file_discovery_example(
        directory_path=str(current_dir),
        pattern=pattern,
        event_bus=event_bus,
        file_processing_service=file_processing_service,
        rich_output=rich_output,
    )

    print("\n🎉 Example completed!")
    print(f"📊 Event bus had {event_bus.get_subscription_count()} active subscriptions")
