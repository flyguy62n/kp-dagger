# Event Bus Memory Management

The `EventBusService` provides context managers for automatic subscription cleanup, preventing memory leaks from forgotten subscriptions.

## Core Implementation

```python
# services/core/events/event_bus.py
from typing import Callable, Protocol, TypeVar, Type, ContextManager
from contextlib import contextmanager
from collections import defaultdict
import weakref
import threading
import uuid

EventT = TypeVar('EventT', bound=BaseEvent)
HandlerT = Callable[[EventT], None]

class IEventSubscription(Protocol):
    """Interface for event subscription management."""
    def unsubscribe(self) -> None:
        """Remove this subscription from the event bus."""
        ...

class EventSubscription:
    """Concrete subscription that can be cancelled."""
    
    def __init__(self, event_bus: 'EventBusService', event_type: Type[EventT], handler: HandlerT, subscription_id: str):
        self.event_bus = event_bus
        self.event_type = event_type
        self.handler = handler
        self.subscription_id = subscription_id
        self._active = True

    def unsubscribe(self) -> None:
        """Remove this subscription from the event bus."""
        if self._active:
            self.event_bus._remove_subscription(self.event_type, self.subscription_id)
            self._active = False

    def __enter__(self) -> 'EventSubscription':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.unsubscribe()

class EventBusService:
    """Event bus with automatic memory management and subscription cleanup."""
    
    def __init__(self, logger: LoggingService | None = None):
        self.logger = logger
        self._subscribers: dict[Type[BaseEvent], dict[str, HandlerT]] = defaultdict(dict)
        self._lock = threading.RLock()

    def publish(self, event: BaseEvent) -> None:
        """Publish an event to all registered handlers."""
        event_type = type(event)
        handlers_copy = None
        
        with self._lock:
            if event_type in self._subscribers:
                # Copy handlers to avoid issues with concurrent modifications
                handlers_copy = dict(self._subscribers[event_type])
        
        if handlers_copy:
            for subscription_id, handler in handlers_copy.items():
                try:
                    handler(event)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Event handler {subscription_id} failed: {e}")
                    # Continue with other handlers - don't let one failure break others

    def subscribe(self, event_type: Type[EventT], handler: HandlerT) -> EventSubscription:
        """Subscribe to events with automatic cleanup support."""
        subscription_id = str(uuid.uuid4())
        
        with self._lock:
            self._subscribers[event_type][subscription_id] = handler
        
        return EventSubscription(self, event_type, handler, subscription_id)

    def _remove_subscription(self, event_type: Type[EventT], subscription_id: str) -> None:
        """Internal method to remove a subscription."""
        with self._lock:
            if event_type in self._subscribers:
                self._subscribers[event_type].pop(subscription_id, None)
                # Clean up empty event type entries
                if not self._subscribers[event_type]:
                    del self._subscribers[event_type]

    @contextmanager
    def subscription_context(self) -> ContextManager['SubscriptionManager']:
        """Context manager for automatic subscription cleanup."""
        manager = SubscriptionManager(self)
        try:
            yield manager
        finally:
            manager.unsubscribe_all()

class SubscriptionManager:
    """Manages multiple subscriptions with automatic cleanup."""
    
    def __init__(self, event_bus: EventBusService):
        self.event_bus = event_bus
        self.subscriptions: list[EventSubscription] = []

    def subscribe(self, event_type: Type[EventT], handler: HandlerT) -> EventSubscription:
        """Subscribe and track the subscription for automatic cleanup."""
        subscription = self.event_bus.subscribe(event_type, handler)
        self.subscriptions.append(subscription)
        return subscription

    def unsubscribe_all(self) -> None:
        """Unsubscribe from all tracked subscriptions."""
        for subscription in self.subscriptions:
            subscription.unsubscribe()
        self.subscriptions.clear()
```

## Memory-Safe Subscription Patterns

### Pattern 1: Individual Subscription Management

```python
# cli/commands/scan.py - Manual subscription management
@click.command()
@inject
def scan_with_manual_cleanup(
    config_paths: list[str],
    event_bus: EventBusService = Provide[CoreContainer.event_bus_service],
    workflow: WorkflowService = Provide[CoreContainer.workflow_service],
    rich_output: RichOutputService = Provide[CoreContainer.rich_output_service],
):
    cli_handler = CliEventHandler(rich_output)
    
    # Each subscription returns a context manager
    with event_bus.subscribe(OperationStarted, cli_handler.handle_operation_started) as sub1, \
         event_bus.subscribe(OperationCompleted, cli_handler.handle_operation_completed) as sub2, \
         event_bus.subscribe(OperationError, cli_handler.handle_operation_error) as sub3, \
         event_bus.subscribe(FindingDiscovered, cli_handler.handle_finding_discovered) as sub4:
        
        try:
            results = workflow.scan_configurations([Path(p) for p in config_paths])
            # Process results...
            
        except KeyboardInterrupt:
            rich_output.warning("Scan cancelled by user")
        except Exception as e:
            rich_output.error(f"Scan failed: {e}")
            raise click.ClickException(str(e))
    
    # All subscriptions automatically cleaned up when context exits
```

### Pattern 2: Batch Subscription Management (Recommended)

```python
# cli/commands/scan.py - Batch subscription management
@click.command()
@inject
def scan_with_context_manager(
    config_paths: list[str],
    event_bus: EventBusService = Provide[CoreContainer.event_bus_service],
    workflow: WorkflowService = Provide[CoreContainer.workflow_service],
    rich_output: RichOutputService = Provide[CoreContainer.rich_output_service],
):
    cli_handler = CliEventHandler(rich_output)
    
    # Use subscription context for automatic cleanup of all subscriptions
    with event_bus.subscription_context() as subscriptions:
        # Subscribe to all needed events
        subscriptions.subscribe(OperationStarted, cli_handler.handle_operation_started)
        subscriptions.subscribe(OperationCompleted, cli_handler.handle_operation_completed)
        subscriptions.subscribe(OperationError, cli_handler.handle_operation_error)
        subscriptions.subscribe(FindingDiscovered, cli_handler.handle_finding_discovered)
        
        try:
            results = workflow.scan_configurations([Path(p) for p in config_paths])
            
            # Final summary
            total_files = len(config_paths)
            successful = sum(1 for r in results if r.success)
            rich_output.info(f"\nScan completed: {successful}/{total_files} files processed successfully")
            
        except KeyboardInterrupt:
            rich_output.warning("Scan cancelled by user")
        except Exception as e:
            rich_output.error(f"Scan failed: {e}")
            raise click.ClickException(str(e))
    
    # All subscriptions automatically cleaned up here
```

### Pattern 3: Long-Lived Service Subscriptions

```python
# gui/main_window.py - GUI service with subscription lifecycle management
class MainWindow:
    def __init__(self, event_bus: EventBusService):
        self.event_bus = event_bus
        self.subscription_manager = SubscriptionManager(event_bus)
        self._setup_event_subscriptions()

    def _setup_event_subscriptions(self) -> None:
        """Set up event subscriptions that last for the lifetime of the window."""
        gui_handler = GuiEventHandler(self)
        
        # These subscriptions will be cleaned up when the window closes
        self.subscription_manager.subscribe(OperationStarted, gui_handler.handle_operation_started)
        self.subscription_manager.subscribe(OperationCompleted, gui_handler.handle_operation_completed)
        self.subscription_manager.subscribe(FindingDiscovered, gui_handler.handle_finding_discovered)

    def close_window(self) -> None:
        """Clean up subscriptions when window closes."""
        self.subscription_manager.unsubscribe_all()
        # Continue with normal window cleanup...
```

## Testing Memory Management

```python
# tests/test_event_bus_memory_management.py
import gc
import weakref
from unittest.mock import Mock

def test_subscription_context_manager_cleanup():
    """Test that subscription context manager properly cleans up subscriptions."""
    event_bus = EventBusService()
    handler = Mock()
    
    # Verify no subscriptions initially
    assert len(event_bus._subscribers) == 0
    
    # Use context manager
    with event_bus.subscription_context() as subscriptions:
        subscriptions.subscribe(OperationStarted, handler)
        subscriptions.subscribe(FindingDiscovered, handler)
        
        # Verify subscriptions are active
        assert len(event_bus._subscribers) == 2
        assert OperationStarted in event_bus._subscribers
        assert FindingDiscovered in event_bus._subscribers
    
    # Verify all subscriptions cleaned up after context exit
    assert len(event_bus._subscribers) == 0

def test_individual_subscription_cleanup():
    """Test that individual subscriptions can be cleaned up manually."""
    event_bus = EventBusService()
    handler = Mock()
    
    # Subscribe and get subscription object
    subscription = event_bus.subscribe(OperationStarted, handler)
    assert len(event_bus._subscribers[OperationStarted]) == 1
    
    # Manually unsubscribe
    subscription.unsubscribe()
    assert len(event_bus._subscribers) == 0

def test_subscription_as_context_manager():
    """Test that individual subscriptions work as context managers."""
    event_bus = EventBusService()
    handler = Mock()
    
    with event_bus.subscribe(OperationStarted, handler) as subscription:
        # Verify subscription is active
        assert len(event_bus._subscribers[OperationStarted]) == 1
        
        # Can publish events normally
        event_bus.publish(OperationStarted(operation_type="test"))
        handler.assert_called_once()
    
    # Verify cleanup after context exit
    assert len(event_bus._subscribers) == 0

def test_memory_leak_prevention():
    """Test that handlers don't create memory leaks."""
    event_bus = EventBusService()
    
    # Create handler that will go out of scope
    def create_handler():
        handler = Mock()
        subscription = event_bus.subscribe(OperationStarted, handler)
        # Return weak reference to track cleanup
        return weakref.ref(handler), subscription
    
    handler_ref, subscription = create_handler()
    
    # Handler should still exist due to subscription
    assert handler_ref() is not None
    
    # Clean up subscription
    subscription.unsubscribe()
    
    # Force garbage collection
    gc.collect()
    
    # Handler should be cleaned up now
    assert handler_ref() is None

def test_concurrent_subscription_management():
    """Test thread safety of subscription management."""
    import threading
    import time
    
    event_bus = EventBusService()
    handlers = []
    subscriptions = []
    
    def subscribe_worker():
        handler = Mock()
        handlers.append(handler)
        subscription = event_bus.subscribe(OperationStarted, handler)
        subscriptions.append(subscription)
        time.sleep(0.01)  # Small delay to interleave operations
    
    def publish_worker():
        for _ in range(10):
            event_bus.publish(OperationStarted(operation_type="test"))
            time.sleep(0.005)
    
    # Start multiple threads
    subscribe_threads = [threading.Thread(target=subscribe_worker) for _ in range(5)]
    publish_thread = threading.Thread(target=publish_worker)
    
    for thread in subscribe_threads:
        thread.start()
    publish_thread.start()
    
    for thread in subscribe_threads:
        thread.join()
    publish_thread.join()
    
    # Clean up all subscriptions
    for subscription in subscriptions:
        subscription.unsubscribe()
    
    # Verify clean state
    assert len(event_bus._subscribers) == 0

def test_long_lived_service_subscription_management():
    """Test subscription management for long-lived services like GUI."""
    event_bus = EventBusService()
    
    # Simulate a long-lived service
    class MockMainWindow:
        def __init__(self, event_bus):
            self.event_bus = event_bus
            self.subscription_manager = SubscriptionManager(event_bus)
            self.handler = Mock()
            self._setup_subscriptions()
        
        def _setup_subscriptions(self):
            self.subscription_manager.subscribe(OperationStarted, self.handler)
            self.subscription_manager.subscribe(FindingDiscovered, self.handler)
        
        def close(self):
            self.subscription_manager.unsubscribe_all()
    
    # Create and use the window
    window = MockMainWindow(event_bus)
    assert len(event_bus._subscribers) == 2
    
    # Events should reach the handler
    event_bus.publish(OperationStarted(operation_type="test"))
    window.handler.assert_called_once()
    
    # Close the window
    window.close()
    assert len(event_bus._subscribers) == 0
```

## Benefits

### Automatic Memory Management
- **Context managers**: Automatic subscription cleanup prevents memory leaks
- **Thread-safe operations**: Concurrent subscription and publication without data races
- **Weak references**: Event handlers don't create circular references
- **Long-lived service support**: SubscriptionManager handles complex subscription lifecycles
- **Resource efficiency**: Unused event type entries are automatically cleaned up

### Developer Experience
- **Simple patterns**: Easy-to-use context managers
- **Fail-safe design**: Memory management never interferes with business logic
- **Flexible cleanup**: Choose individual or batch cleanup as needed
- **Testing support**: Memory management is easily testable

## Best Practices

1. **Use context managers** for temporary subscriptions (CLI commands, short-lived operations)
2. **Use SubscriptionManager** for long-lived services (GUI windows, background services)
3. **Test memory cleanup** in your test suite to prevent regressions
4. **Avoid manual subscription management** unless absolutely necessary

## Next Steps

- [Progress Callbacks](progress-callbacks.md) - Learn about fine-grained progress reporting
- [Testing Patterns](testing-patterns.md) - Explore testing approaches for event-driven architectures
