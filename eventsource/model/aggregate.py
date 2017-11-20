from collections import deque

import time
from typing import Deque

from eventsource.model.entity import TimestampedVersionedEntity
from eventsource.model.events import DomainEvent


class AggregateRoot(TimestampedVersionedEntity):
    _pending_events: Deque[DomainEvent]

    """
    Root entity for an aggregate in a domain driven design.
    """

    class Event(TimestampedVersionedEntity.Event):
        """Layer supertype."""

    class Created(Event, TimestampedVersionedEntity.Created):
        """Published when an AggregateRoot is created."""

    class AttributeChanged(Event, TimestampedVersionedEntity.AttributeChanged):
        """Published when an AggregateRoot is changed."""

    class Discarded(Event, TimestampedVersionedEntity.Discarded):
        """Published when an AggregateRoot is discarded."""

    def __init__(self, **kwargs):
        super(AggregateRoot, self).__init__(**kwargs)
        self._pending_events = deque()

    @staticmethod
    def _static_publish(cls, event):
        entity = cls._mutate(initial=None, event=event)
        entity._pending_events.append(event)
        return entity

    def _apply(self, cls: type, **kwargs) -> None:
        self._publish(cls(
            originator_version=self.version,
            timestamp=time.time(),
            originator_id=self.id, **kwargs))

    def _publish_mutated(self, event: DomainEvent) -> None:
        self._pending_events.append(event)

    def _publish(self, event: DomainEvent) -> None:
        """
        Appends event to internal collection of pending events.
        """
        self._mutate(initial=self, event=event)
        self._increment_version()
        self._pending_events.append(event)

    def _apply_and_publish(self, event):
        self._mutate(initial=self, event=event)
        self._pending_events.append(event)
        return self

    def flush(self):
        """
        Publishes pending events for others in application.
        """
        batch_of_events = []
        try:
            while True:
                batch_of_events.append(self._pending_events.popleft())
        except IndexError:
            pass
        if batch_of_events:
            return batch_of_events
