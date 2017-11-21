import asyncio
import uuid
import asynctest
from os import environ

from peewee_async import Manager, PooledPostgresqlDatabase

from eventsource.ext.pewee_active_record_strategy import PeweeActiveRecordStrategy, EventRecord
from tests.application import ToDoAggregate, ToDoApplication


class TodoDbTest(asynctest.TestCase):
    use_default_loop = True

    def setUp(self):
        self.db = PooledPostgresqlDatabase(
            database=environ.get('PGDB', 'postgres'),
            user=environ.get('PGUSER', 'admin'),
            password=environ.get('PGPASS', 'admin'))
        self.db_manager = Manager(database=self.db)
        self.ar_strategy = PeweeActiveRecordStrategy(
            manager=self.db_manager,
            active_record_class=EventRecord
        )
        self.app = ToDoApplication(entity_active_record_strategy=self.ar_strategy, )

    async def perf_press(self):
        tasks = []
        for i in range(1, 10):
            tasks.append(self.make_todo(i))

        await asyncio.wait(tasks)

    async def test_todo_with_db(self):
        await self.make_todo()

    async def make_todo(self, index=0):
        id = uuid.uuid4()
        task_len = 10
        todo_item = ToDoAggregate.create_todos(id)
        self.assertEqual(todo_item.id, id)
        await self.app.todos.save(todo_item)

        events = await self.app.todos.event_store.get_domain_events(originator_id=id)
        self.assertEqual(len(events), 1)
        todo_item = await self.app.todos.get_entity(id)
        self.assertEqual(todo_item.id, id)
        todo_item.todo_name = str(id)
        for task_index in range(0, task_len):
            todo_item.add_item('todo_item #' + str(task_index) + '-' + str(index))

        await self.app.todos.save(todo_item)
        todo_item = await self.app.todos.get_entity(id)
        self.assertEqual(len(todo_item.items), task_len)
        self.assertEqual(todo_item.todo_name, str(id))

    def tearDown(self):
        self.app.close()
