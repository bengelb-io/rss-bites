from db import Entry, Summary
from peewee import Select

def latest_summaries(n: int = 10):
    selection : Select= Entry.select(Entry, Summary)
    return (
        selection
            .join(Summary)
            .order_by()
            .limit(n)
        )