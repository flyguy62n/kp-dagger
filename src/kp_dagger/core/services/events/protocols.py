"""Event service protocols for publish-subscribe patterns."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from kp_dagger.models.events import BaseEvent, EventT


class EventPublisher(Protocol):
    """Protocol for event publishing interfaces."""

    def publish(self, event: BaseEvent) -> None:
        """
        Publish an event to subscribers.

        Args:
            event: The event to publish

        """
        ...


class EventSubscriber(Protocol):
    """Protocol for event subscription management."""

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
        ...

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
        ...


class EventBus(EventPublisher, EventSubscriber, Protocol):
    """Protocol for full event bus functionality."""

    def clear_subscriptions(self) -> None:
        """Clear all event subscriptions."""
        ...

    def get_subscription_count(self, event_type: type[BaseEvent] | None = None) -> int:
        """
        Get the number of active subscriptions.

        Args:
            event_type: Specific event type to count, or None for total

        Returns:
            Number of active subscriptions

        """
        ...
