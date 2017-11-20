from typing import List

import six
from eventsource.services.activerecord import AbstractActiveRecordStrategy
from eventsource.services.sequenceditem import SequencedItem


class InPlaceActiveRecordStrategy(AbstractActiveRecordStrategy):
    dumb_store = []

    def __init__(self, *args, **kwargs):
        super(InPlaceActiveRecordStrategy, self).__init__(*args, **kwargs)
        self.field_names = SequencedItem

    async def append(self, sequenced_item_or_items):
        if isinstance(sequenced_item_or_items, list):
            records = sequenced_item_or_items
        else:
            records = [sequenced_item_or_items]

        self.dumb_store.extend(records)

    async def get_item(self, sequence_id, eq):
        return next(x for x in self.dumb_store if
                    x[1] == eq
                    and x[0] == sequence_id)

    async def get_items(self, sequence_id, gt=None, gte=None, lt=None, lte=None, limit=None,
                        query_ascending=True, results_ascending=True):
        assert limit is None or limit >= 1, limit
        events = sorted(filter(lambda x: x[0] == sequence_id, self.dumb_store),
                        key=lambda x: x[1],
                        reverse=not query_ascending)
        return events

    async def all_items(self):
        """
        Returns all items across all sequences.
        """
        return self.dumb_store

    async def all_records(self, resume=None, *args, **kwargs) -> List:
        """
        Returns all records in the table.
        """
        return self.dumb_store

    async def delete_record(self, record):
        """
        Permanently removes record from table.
        """
        pass
