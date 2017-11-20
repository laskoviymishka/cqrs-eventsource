import asyncio
import unittest
import uuid
from os import environ

from aiounittest import async_test
from peewee_async import Manager, PostgresqlDatabase

from eventsource.ext.pewee_active_record_strategy import PeweeActiveRecordStrategy, EventRecord
from tests.application import ToDoAggregate, ToDoApplication


class TodoDbTest(unittest.TestCase):
    def setUp(self):
        self.ar_strategy = PeweeActiveRecordStrategy(
            manager=Manager(PostgresqlDatabase(
                database=environ.get('PGDB', 'postgres'),
                user=environ.get('PGUSER', 'admin'),
                password=environ.get('PGPASS', 'admin'))),
            active_record_class=EventRecord
        )
        self.app = ToDoApplication(entity_active_record_strategy=self.ar_strategy, )

    @async_test
    async def perf_press(self):
        tasks = []
        for i in range(1, 10):
            tasks.append(self.make_todo())

        await asyncio.wait(tasks)

    async def make_todo(self):
        id = uuid.uuid4()
        task_len = 10
        todo_item = ToDoAggregate.create_todos(id)
        self.assertEqual(todo_item.id, id)

        await self.app.todos.save(todo_item)
        todo_item = await self.app.todos.get_entity(id)
        todo_item.todo_name = str(id)
        for task_index in range(0, task_len):
            todo_item.add_item('todo_item #' + str(task_index))

        await self.app.todos.save(todo_item)
        todo_item = await self.app.todos.get_entity(id)
        self.assertEqual(len(todo_item.items), task_len)
