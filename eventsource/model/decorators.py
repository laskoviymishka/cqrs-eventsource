from inspect import isfunction
from random import random
from time import sleep
from functools import singledispatch

from six import wraps

from eventsource.exceptions import ProgrammingError
from eventsource.model.events import subscribe


def subscribe_to(event_class):
    """
    Decorator for making a custom event handler function subscribe to a certain event type

    event_class: DomainEvent class or its child classes that the handler function should subscribe to

    The following example shows a custom handler that reacts to Todo.Created
    event and saves a projection of a Todo model object.

    .. code::

        @subscribe_to(Todo.Created)
        def new_todo_projection(event):
            todo = TodoProjection(id=event.originator_id, title=event.title)
            todo.save()
    """

    def event_type_predicate(event):
        return isinstance(event, event_class)

    def wrap(handler_func):
        subscribe(handler_func, event_type_predicate)
        return handler_func

    return wrap


def mutator(arg=None):
    """Structures mutator functions by allowing handlers
    to be registered for different types of event. When
    the decorated function is called with an initial
    value and an event, it will call the handler that
    has been registered for that type of event.

    It works like singledispatch, which it uses. The
    difference is that when the decorated function is
    called, this decorator dispatches according to the
    type of last call arg, which fits better with reduce().
    The builtin Python function reduce() is used by the
    library to replay a sequence of events against an
    initial state. If a mutator function is given to reduce(),
    along with a list of events and an initializer, reduce()
    will call the mutator function once for each event in the
    list, but the initializer will be the first value, and the
    event will be the last argument, and we want to dispatch
    according to the type of the event. It happens that
    singledispatch is coded to switch on the type of the first
    argument, which makes it unsuitable for structuring a mutator
    function without the modifications introduced here.

    The other aspect introduced by this decorator function is the
    option to set the type of the handled entity in the decorator.
    When an entity is replayed from scratch, in other words when
    all its events are replayed, the initial state is None. The
    handler which handles the first event in the sequence will
    probably construct an object instance. It is possible to write
    the type into the handler, but that makes the entity more difficult
    to subclass because you will also need to write a handler for it.
    If the decorator is invoked with the type, when the initial
    value passed as a call arg to the mutator function is None,
    the handler will instead receive the type of the entity, which
    it can use to construct the entity object.

    .. code::

        class Entity(object):
            class Created(object):
                pass

        @mutator(Entity)
        def mutate(initial, event):
            raise NotImplementedError(type(event))

        @mutate.register(Entity.Created)
        def _(initial, event):
            return initial(**event.__dict__)

        entity = mutate(None, Entity.Created())
    """

    domain_class = None

    def _mutator(func):
        wrapped = singledispatch(func)

        @wraps(wrapped)
        def wrapper(initial, event):
            initial = initial or domain_class
            return wrapped.dispatch(type(event))(initial, event)

        wrapper.register = wrapped.register

        return wrapper

    if isfunction(arg):
        return _mutator(arg)
    else:
        domain_class = arg
        return _mutator


def event_generator(arg: type):
    def _handler(func):
        def _handler_wrapper(self, *args, **kwargs):
            self._apply(arg, **kwargs)

        return _handler_wrapper

    return _handler


def attribute(getter):
    """
    When used as a method decorator, returns a property object
    with the method as the getter and a setter defined to call
    instance method change_attribute(), which publishes an
    AttributeChanged event.
    """
    if isfunction(getter):
        def setter(self, value):
            name = '_' + getter.__name__
            self.change_attribute(name=name, value=value)

        def new_getter(self):
            name = '_' + getter.__name__
            return getattr(self, name)

        return property(fget=new_getter, fset=setter, doc=getter.__doc__)
    else:
        raise ProgrammingError("Expected a function, got: {}".format(repr(getter)))
