import inspect

from abc import abstractmethod, ABCMeta
from typing import Generic, TypeVar, Dict, Callable

TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')


class Command(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


class AggregateCommand(Command, metaclass=ABCMeta):
    def __init__(self, originator_id, **kwargs):
        self.originator_id = originator_id
        super().__init__(**kwargs)


class CommandHandler(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    @abstractmethod
    async def handle(self, command: Command) -> None: ...


class FunctionBaseHandler(CommandHandler):
    def __init__(self, func: Callable, **kwargs):
        self.func = func
        super().__init__(**kwargs)

    async def handle(self, command: Command):
        await self.func(command, **self.__dict__)


class QuerySpec(Generic[TInput, TOutput], metaclass=ABCMeta):
    def __init__(self, data: TInput):
        self.data: TInput = data


class QueryProcessor(Generic[TInput, TOutput], metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    @abstractmethod
    async def run(self, query: QuerySpec[TInput, TOutput]) -> TOutput: ...


class FunctionBaseProcessor(QueryProcessor[TInput, TOutput]):
    def __init__(self, func: Callable, **kwargs):
        self.func = func
        super().__init__(**kwargs)

    async def run(self, query: QuerySpec[TInput, TOutput]):
        return await self.func(query, **self.__dict__)


class BusResolverError(BaseException): ...


_QUERY_HANDLERS: Dict[type, Callable] = {}
_COMMAND_HANDLERS: Dict[type, Callable] = {}


def command_handler(command_cls: type):
    def decorator(func):
        if inspect.isclass(func):
            _COMMAND_HANDLERS[command_cls] = func
        else:
            def factory(**kwargs):
                return FunctionBaseHandler(func, **kwargs)

            _COMMAND_HANDLERS[command_cls] = factory

        return func

    return decorator


def query_processor(query_cls: type):
    def decorator(func):
        if inspect.isclass(func):
            _QUERY_HANDLERS[query_cls] = func
        else:
            def factory(**kwargs):
                return FunctionBaseProcessor(func, **kwargs)

            _QUERY_HANDLERS[query_cls] = factory

        return func

    return decorator


class Bus(object):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    async def run_query(self, query: QuerySpec) -> TOutput:
        if type(query) not in _QUERY_HANDLERS.keys():
            raise BusResolverError

        handler = _QUERY_HANDLERS[type(query)](**self.__dict__)
        return await handler.run(query)

    async def execute_command(self, command: Command) -> None:
        if type(command) not in _COMMAND_HANDLERS.keys():
            raise BusResolverError

        handler = _COMMAND_HANDLERS[type(command)](**self.__dict__)
        await handler.handle(command)
