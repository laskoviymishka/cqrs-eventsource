from typing import List, overload

from peewee_async import Manager

from eventsource.application.base import ApplicationWithPersistencePolicies
from eventsource.model.aggregate import AggregateRoot
from eventsource.model.decorators import mutator, attribute, event_generator
from eventsource.model.entity import mutate_entity, AbstractEntityRepository
from eventsource.model.events import EventSession
from eventsource.services.eventsourcedrepository import EventSourcedRepository
from eventsource.services.snapshotting import EventSourcedSnapshotStrategy


class ToDoItem:
    def __init__(self, item_id: int, name: str, is_completed: bool):
        self.name = name
        self.is_completed = is_completed
        self.id = item_id


@mutator
def todos_mutator(initial, event, ):
    return mutate_entity(initial, event)


class ToDoAggregate(AggregateRoot):
    __items: List[ToDoItem] = []
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__items = []

    class Event(AggregateRoot.Event):
        """ layer supertype """

    class Created(AggregateRoot.Created):
        """ todo layer created event """

    class ToDoAdded(Event):
        name: str
        item_id: int

    class CompletedCleaned(Event):
        """ event for cleanup completed events """

    class ItemUncompleted(Event):
        item_id: int

    class ItemCompleted(Event):
        item_id: int

    @property
    def items(self) -> List[ToDoItem]:
        return self.__items

    @property
    def __max_id(self) -> int:
        if len(self.__items) == 0: return 0
        return max(map(lambda x: x.id, self.__items))

    @classmethod
    def create_todos(cls, originator_id, **kwargs) -> 'ToDoAggregate':
        return ToDoAggregate._static_publish(
            cls=ToDoAggregate,
            event=ToDoAggregate.Created(originator_id=originator_id, **kwargs)
        )

    @classmethod
    def _mutate(cls, initial, event):
        return todos_mutator(initial or cls, event)

    @attribute
    def todo_name(self):
        """ the name of todos """

    def add_item(self, name: str) -> None:
        self._apply(ToDoAggregate.ToDoAdded, item_id=self.__max_id + 1, name=name)

    @event_generator(ItemCompleted)
    def complete_item(self, item_id: int) -> None:
        """ complete single item """

    @event_generator(ItemUncompleted)
    def uncomplete_item(self, item_id: int) -> None:
        """ uncomplete single item """

    @event_generator(CompletedCleaned)
    def clean_completed(self):
        """ cleanup completed items """

    @todos_mutator.register(ToDoAdded)
    def __add(self, event: ToDoAdded) -> 'ToDoAggregate':
        self.__items.append(ToDoItem(event.item_id, event.name, False))
        return self

    @todos_mutator.register(ItemCompleted)
    def __complete(self, event: ItemCompleted) -> 'ToDoAggregate':
        for item in self.__items:
            if item.id == event.item_id:
                item.is_completed = True
        return self

    @todos_mutator.register(ItemUncompleted)
    def __un_complete(self, event: ItemUncompleted) -> 'ToDoAggregate':
        for item in self.__items:
            if item.id == event.item_id:
                item.is_completed = False
        return self

    @todos_mutator.register(CompletedCleaned)
    def __clean(self, event: CompletedCleaned) -> 'ToDoAggregate':
        items = []
        for item in self.__items:
            if not item.is_completed:
                items.append(item)

        self.__items = items
        return self


def mutate_clean_completed(self, event: ToDoAggregate.ItemUncompleted) -> None:
    pass


class ToDoRepository(EventSourcedRepository[ToDoAggregate]):
    mutator = ToDoAggregate._mutate


class ToDoApplication(ApplicationWithPersistencePolicies):
    todos: ToDoRepository

    def __init__(self, **kwargs):
        super(ToDoApplication, self).__init__(**kwargs)
        self.snapshot_strategy = None
        if self.snapshot_event_store:
            self.snapshot_strategy = EventSourcedSnapshotStrategy(event_store=self.snapshot_event_store)
        assert self.entity_event_store is not None
        self.todos = ToDoRepository(
            event_store=self.entity_event_store,
            event_session=EventSession(**kwargs),
            snapshot_strategy=self.snapshot_strategy, )
