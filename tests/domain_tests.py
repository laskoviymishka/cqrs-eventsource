import unittest

from tests.application import ToDoAggregate


class TodoDomainTest(unittest.TestCase):
    def test_todo_created(self):
        todo_app = ToDoAggregate.create_todos(originator_id=1)

        self.assertEqual(len(todo_app.items), 0)
        self.assertEqual(todo_app.id, 1)
        self.assertEqual(todo_app.version, 1)

    def test_todo_should_add_item(self):
        todo_app = ToDoAggregate.create_todos(originator_id=1)
        todo_app.add_item('test todo')

        self.assertEqual(len(todo_app.items), 1)

    def test_todo_should_complete_item(self):
        todo_app = ToDoAggregate.create_todos(originator_id=1)
        todo_app.add_item('test todo')
        todo_app.complete_item(item_id=1)

        self.assertEqual(todo_app.items[0].is_completed, True)

    def test_todo_should_uncomplete_completed_item(self):
        todo_app = ToDoAggregate.create_todos(originator_id=1)
        todo_app.add_item('test todo')
        todo_app.complete_item(item_id=1)

        self.assertEqual(todo_app.items[0].is_completed, True)
        todo_app.uncomplete_item(item_id=1)
        self.assertEqual(todo_app.items[0].is_completed, False)

    def test_todo_should_clean_completed_items(self):
        todo_app = ToDoAggregate.create_todos(originator_id=1)
        todo_app.add_item('test todo1')
        todo_app.add_item('test todo2')
        todo_app.add_item('test todo3')

        todo_app.complete_item(item_id=2)
        todo_app.clean_completed()

        self.assertEqual(len(todo_app.items), 2)
        self.assertEqual(todo_app.items[0].id, 1)
        self.assertEqual(todo_app.items[1].id, 3)

    def test_todo_should_have_all_events(self):
        todo_app = ToDoAggregate.create_todos(originator_id=1)
        todo_app.add_item('test todo')
        todo_app.complete_item(item_id=1)
        todo_app.clean_completed()

        events = todo_app.flush()
        self.assertEqual(len(events), 4)
