from six import moves
from builtins import list
from peewee_async import execute
from builtins import BaseException
from playhouse.postgres_ext import JSONField
from peewee import *
from eventsource.services.activerecord import AbstractActiveRecordStrategy


class PeweeActiveRecordStrategy(AbstractActiveRecordStrategy):
    def __init__(self, manager, *args, **kwargs):
        self.manager = manager
        EventRecord._meta.database = self.manager.database
        if not EventRecord.table_exists():
            EventRecord.create_table()

        super(PeweeActiveRecordStrategy, self).__init__(*args, **kwargs)

    async def append(self, sequenced_item_or_items):
        if isinstance(sequenced_item_or_items, list):
            active_records = [self.to_active_record(i) for i in sequenced_item_or_items]
        else:
            active_records = [self.to_active_record(sequenced_item_or_items)]

        for record in active_records:
            await self.manager.create(EventRecord, **record)

    async def get_item(self, sequence_id, eq):
        return await EventRecord \
            .select() \
            .where(EventRecord.sequence_id == sequence_id and EventRecord.position == eq)

    async def get_items(self, sequence_id, gt=None, gte=None, lt=None, lte=None, limit=None,
                        query_ascending=True, results_ascending=True):
        query = EventRecord.select().where(EventRecord.sequence_id == sequence_id)
        if gt is not None:
            query = query.where(EventRecord.position > gt)
        if gte is not None:
            query = query.where(EventRecord.position >= gte)
        if lt is not None:
            query = query.where(EventRecord.position < lt)
        if lte is not None:
            query = query.where(EventRecord.position <= lte)

        if limit is not None:
            query = query.limit(limit)

        if query_ascending:
            query = query.order_by(EventRecord.position.asc())
        else:
            query = query.order_by(EventRecord.position.desc())

        events = moves.map(self.from_active_record, query)
        events = list(events)
        return events

    async def all_items(self):
        return await execute(EventRecord.select())

    async def all_records(self, resume=None, *args, **kwargs):
        return await execute(EventRecord.select())

    async def delete_record(self, record):
        await execute(EventRecord.delete_instance(record))

    def init(self):
        EventRecord._meta.database = self.manager.database
        EventRecord.create_table(True)

    def to_active_record(self, item):
        return {
            'sequence_id': item.sequence_id,
            'position': item.position,
            'topic': item.topic,
            'data': item.data
        }

    def from_active_record(self, item):
        kwargs = self.get_field_kwargs(item)
        return self.sequenced_item_class(**kwargs)


class EventRecord(Model):
    sequence_id = UUIDField()
    position = BigIntegerField()
    topic = CharField(max_length=255)
    data = JSONField()

    class Meta:
        db_table = 'es_int_events'
        primary_key = CompositeKey('sequence_id', 'position')
