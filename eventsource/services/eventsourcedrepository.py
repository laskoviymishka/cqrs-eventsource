from typing import TypeVar

from eventsource.model.entity import AbstractEntityRepository, mutate_entity, DomainEntity
from eventsource.model.events import EventSession
from eventsource.services.eventstore import EventStore
from eventsource.services.snapshotting import entity_from_snapshot
from eventsource.services.eventplayer import EventPlayer
from eventsource.exceptions import RepositoryKeyError
from eventsource.services.eventstore import AbstractEventStore

T = TypeVar('T')


class EventSourcedRepository(AbstractEntityRepository[T]):
    # If the entity won't have very many events, marking the entity as
    # "short" by setting __is_short__ value equal to True will mean
    # the fastest path for getting all the events is used. If you set
    # a value for page size (see below), this option will have no effect.
    __is_short__ = False

    # The page size by which events are retrieved. If this
    # value is set to a positive integer, the events of
    # the entity will be retrieved in pages, using a series
    # of queries, rather than with one potentially large query.
    __page_size__ = None

    # The mutator function used by this repository. Can either
    # be set as a class attribute, or passed as a constructor arg.
    mutator = mutate_entity

    def __init__(self,
                 event_session: EventSession,
                 event_store: AbstractEventStore,
                 mutator=None,
                 snapshot_strategy=None,
                 use_cache=False,
                 *args,
                 **kwargs):
        super(EventSourcedRepository, self).__init__(*args, **kwargs)
        self.event_session = event_session
        self._cache = {}
        self._snapshot_strategy = snapshot_strategy
        # self._use_cache = use_cache

        # Check we got an event store.
        assert isinstance(event_store, AbstractEventStore), type(event_store)
        self._event_store = event_store

        # Instantiate an event player for this repo.
        mutator = mutator or type(self).mutator
        self.event_player = EventPlayer(
            event_store=self.event_store,
            mutator=mutator,
            page_size=self.__page_size__,
            is_short=self.__is_short__,
            snapshot_strategy=self._snapshot_strategy,
        )

    @property
    def event_store(self):
        return self._event_store

    async def contains(self, entity_id) -> bool:
        """
        Returns a boolean value according to whether entity with given ID exists.
        """
        return await self.get_entity(entity_id) is not None

    async def get_entity(self, entity_id, lt=None, lte=None) -> T:
        """
        Returns entity with given ID, optionally until position.
        """

        # Get a snapshot (None if none exist).
        if self._snapshot_strategy is not None:
            snapshot = self._snapshot_strategy.get_snapshot(entity_id, lt=lt, lte=lte)
        else:
            snapshot = None

        # Decide the initial state of the entity, and the
        # version of the last item applied to the entity.
        if snapshot is None:
            initial_state = None
            gt = None
        else:
            initial_state = entity_from_snapshot(snapshot)
            gt = snapshot.originator_version

        # Replay domain events.
        return await self.event_player.replay_entity(entity_id, gt=gt, lt=lt, lte=lte, initial_state=initial_state)

    def take_snapshot(self, entity_id, lt=None, lte=None):
        return self.event_player.take_snapshot(entity_id, lt=lt, lte=lte)

    async def save(self, entity: T) -> None:
        await self.event_session.save(entity=entity)
