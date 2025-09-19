"""Event bus service with subscription management and safe publishing."""

from __future__ import annotations

import contextlib
import weakref
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from kp_dagger.core.services.events.protocols import EventPublisher
    from kp_dagger.models.events import BaseEvent, EventT


class NullEventPublisher:
    """No-op implementation for services that don't need events."""

    def publish(self, event: BaseEvent) -> None:
        """
        No-op publish implementation.

        Args:
            event: The event to ignore

        """


class SafeEventPublisher:
    """Wrapper that makes event publishing safe and eliminates boilerplate."""

    def __init__(self, publisher: EventPublisher | None = None) -> None:
        """
        Initialize the safe event publisher.

        Args:
            publisher: The underlying event publisher (uses NullEventPublisher if None)

        """
        self.publisher = publisher or NullEventPublisher()

    def publish(self, event: BaseEvent) -> None:
        """
        Safely publish events with automatic error handling.

        Args:
            event: The event to publish

        """
        with contextlib.suppress(Exception):
            # Never let event publishing break business logic
            self.publisher.publish(event)


class EventBusService:
    """
    Event bus service with subscription management and memory-safe cleanup.

    Provides publish-subscribe functionality with automatic weak reference
    management to prevent memory leaks.
    """

    def __init__(self) -> None:
        """Initialize the event bus with empty subscriptions."""
        self._subscribers: dict[type[BaseEvent], list[weakref.WeakMethod]] = (
            defaultdict(list)
        )

    def publish(self, event: BaseEvent) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: The event to publish

        """
        event_type = type(event)

        # Get subscribers and clean up dead references
        subscribers = self._subscribers[event_type]
        active_subscribers = []

        for weak_handler in subscribers:
            handler = weak_handler()
            if handler is not None:
                active_subscribers.append(weak_handler)
                # Safely call handler - never let subscriber errors break publishing
                with contextlib.suppress(Exception):
                    handler(event)

        # Update list with only active subscribers
        self._subscribers[event_type] = active_subscribers

    def subscribe(
        self,
        event_type: type[EventT],
        handler: Callable[[EventT], None],
    ) -> None:
        """
        Subscribe to events of a specific type.

        Args:
            event_type: The type of event to subscribe to
            handler: The callback function to handle the event

        """
        # Use weak references to prevent memory leaks
        weak_handler = weakref.WeakMethod(handler)
        self._subscribers[event_type].append(weak_handler)

    def unsubscribe(
        self,
        event_type: type[EventT],
        handler: Callable[[EventT], None],
    ) -> None:
        """
        Unsubscribe from events of a specific type.

        Args:
            event_type: The type of event to unsubscribe from
            handler: The callback function to remove

        """
        subscribers = self._subscribers[event_type]

        # Find and remove the handler
        for i, weak_handler in enumerate(subscribers):
            if weak_handler() == handler:
                del subscribers[i]
                break

    def clear_subscriptions(self) -> None:
        """Clear all event subscriptions."""
        self._subscribers.clear()

    def get_subscription_count(self, event_type: type[BaseEvent] | None = None) -> int:
        """
        Get the number of active subscriptions.

        Args:
            event_type: Specific event type to count, or None for total

        Returns:
            Number of active subscriptions

        """
        if event_type is not None:
            # Clean up dead references first
            subscribers = self._subscribers[event_type]
            active_count = sum(1 for weak_ref in subscribers if weak_ref() is not None)
            return active_count

        # Count all active subscriptions across all event types
        total = 0
        for subscribers in self._subscribers.values():
            total += sum(1 for weak_ref in subscribers if weak_ref() is not None)

        return total
