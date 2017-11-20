import unittest

from aiounittest import async_test

from eventsource.ext.inplaceactiverecordstrategy import InPlaceActiveRecordStrategy
from eventsource.model.decorators import subscribe_to
from eventsource.services.sequenceditem import SequencedItemFieldNames
from tests.application import ToDoAggregate, ToDoApplication


class TodoApplicationTest(unittest.TestCase):
    def setUp(self):
        self.ar_strategy = InPlaceActiveRecordStrategy(active_record_class=SequencedItemFieldNames)
        self.app = ToDoApplication(entity_active_record_strategy=self.ar_strategy, )

    @async_test
    async def test_todo_created(self):
        todo_item = ToDoAggregate.create_todos(1)
        self.assertEqual(todo_item.id, 1)

        await self.app.todos.save(todo_item)
        todo_item = await self.app.todos.get_entity(1)
        self.assertEqual(todo_item.id, 1)
        events = await self.app.todos.event_store.get_domain_events(1)
        self.assertEqual(len(events), 1)

    @async_test
    async def test_todo_should_add_item(self):
        todo_item = ToDoAggregate.create_todos(2)
        await self.app.todos.save(todo_item)
        todo_item = await self.app.todos.get_entity(2)
        todo_item.add_item('test item')
        await self.app.todos.save(todo_item)

        todo_item = await self.app.todos.get_entity(2)
        self.assertEqual(todo_item.items[0].name, 'test item')
        events = await self.app.todos.event_store.get_domain_events(2)
        self.assertEqual(len(events), 2)

    @async_test
    async def test_subscribe_to(self):
        test_var = False

        @subscribe_to(ToDoAggregate.Created)
        async def test_subs(event, **kwargs):
            nonlocal test_var
            test_var = True

        todo_item = ToDoAggregate.create_todos(4)
        await self.app.todos.save(todo_item)
        self.assertEqual(test_var, True)

    @async_test
    async def test_todo_should_be_able_to_change_attribute(self):
        todo_item = ToDoAggregate.create_todos(3)
        await self.app.todos.save(todo_item)
        todo_item = await self.app.todos.get_entity(3)
        todo_item.todo_name = 'test name'
        await self.app.todos.save(todo_item)

        todo_item = await self.app.todos.get_entity(3)
        self.assertEqual(todo_item.todo_name, 'test name')
        events = await self.app.todos.event_store.get_domain_events(3)
        self.assertEqual(len(events), 2)
