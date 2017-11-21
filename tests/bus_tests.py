import unittest

from aiounittest import async_test

from eventsource.services.commandbus import Command, command_handler, Bus, QuerySpec, query_processor, BusResolverError, \
    AggregateCommand, CommandHandler, QueryProcessor


class BusTests(unittest.TestCase):
    @async_test
    async def test_command_handler_should_called(self):
        was_called = False

        class TestCommand(Command): ...

        @command_handler(TestCommand)
        async def test_command_function(command: TestCommand, **kwargs):
            nonlocal was_called
            self.assertIsNotNone(command)
            was_called = True

        bus = Bus()
        await bus.execute_command(TestCommand())
        self.assertTrue(was_called)

    @async_test
    async def test_command_should_pass_argument_from_bus_constructor(self):
        was_called = False

        class TestCommand(Command): ...

        @command_handler(TestCommand)
        async def test_command_function(command: TestCommand, test_data: bool, **kwargs):
            nonlocal was_called
            was_called = test_data

        bus = Bus(test_data=True)
        await bus.execute_command(TestCommand())
        self.assertTrue(was_called)

    @async_test
    async def test_command_should_raise_argument_error_when_bus_not_have_one(self):
        class TestCommand(Command):
            ...

        @command_handler(TestCommand)
        async def test_command_function(query: TestCommand, not_exist_data: bool, **kwargs):
            ...

        error_raised = False
        bus = Bus(test_data=True)
        try:
            await bus.execute_command(TestCommand())
        except TypeError:
            error_raised = True

        self.assertTrue(error_raised)

    @async_test
    async def test_query_handler_should_return(self):
        class TestQuery(QuerySpec[bool, bool]): ...

        @query_processor(TestQuery)
        async def test_query_processor(query: TestQuery, **kwargs) -> bool:
            self.assertTrue(query.data)
            return True

        bus = Bus()
        res = await bus.run_query(TestQuery(True))
        self.assertTrue(res)

    @async_test
    async def test_query_should_pass_argument_from_bus_constructor(self):
        class TestQuery(QuerySpec[bool, bool]): ...

        @query_processor(TestQuery)
        async def test_query_processor(query: TestQuery, test_data: bool, **kwargs) -> bool:
            return test_data

        bus = Bus(test_data=True)
        self.assertTrue(await bus.run_query(TestQuery(True)))

    @async_test
    async def test_query_should_raise_argument_error_when_bus_not_have_one(self):
        class TestQuery(QuerySpec[bool, bool]):
            ...

        @query_processor(TestQuery)
        async def test_query_processor(query: TestQuery, not_exist_data: bool, **kwargs) -> bool:
            return True

        error_raised = False
        bus = Bus(test_data=True)
        try:
            await bus.run_query(TestQuery(True))
        except TypeError:
            error_raised = True

        self.assertTrue(error_raised)

    @async_test
    async def test_command_should_raise_when_command_not_handled(self):
        class TestCommand(Command):
            ...

        error_raised = False
        bus = Bus()
        try:
            await bus.execute_command(TestCommand())
        except BusResolverError:
            error_raised = True

        self.assertTrue(error_raised)

    @async_test
    async def test_query_should_raise_when_command_not_handled(self):
        class TestQuery(QuerySpec[bool, bool]):
            ...

        error_raised = False
        bus = Bus()
        try:
            await bus.run_query(TestQuery(True))
        except BusResolverError:
            error_raised = True

        self.assertTrue(error_raised)

    @async_test
    async def test_aggregate_command_should_pass_originator(self):
        class TestAggregateCommand(AggregateCommand): ...

        passed_id = -1
        expected_id = 123

        @command_handler(TestAggregateCommand)
        async def test_handler(command: TestAggregateCommand, **kwargs):
            nonlocal passed_id
            passed_id = command.originator_id

        bus = Bus()
        await bus.execute_command(TestAggregateCommand(originator_id=expected_id))
        self.assertEqual(expected_id, passed_id)

    @async_test
    async def test_class_command_handler_should_executer(self):
        class TestCommand(Command): ...

        called = False

        @command_handler(TestCommand)
        class TestHandler(CommandHandler):
            async def handle(self, command: TestCommand):
                nonlocal called
                called = True

        bus = Bus()
        await bus.execute_command(TestCommand())
        self.assertTrue(called)

    @async_test
    async def test_class_query_processor_should_executer(self):
        class TestQuery(QuerySpec[bool, bool]): ...

        called = False

        @query_processor(TestQuery)
        class TestProcessor(QueryProcessor[bool, bool]):
            async def run(self, query: TestQuery):
                nonlocal called
                called = True
                return query.data

        bus = Bus()
        await bus.run_query(TestQuery(True))
        self.assertTrue(called)
