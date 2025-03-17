from peewee import (
    Model,
    SqliteDatabase,
    ForeignKeyField,
    CharField,
    IntegerField,
    TextField,
    DateTimeField,
    TimestampField,
)

from datetime import datetime

db = SqliteDatabase("bite.db")


class BaseModel(Model):
    class Meta:
        database = db


class Entry(BaseModel):

    # RSS Fields
    title = CharField(max_length=255)
    link = TextField()
    description = TextField()
    published = DateTimeField()
    guid = TextField(unique=True, index=True)

    # Metadata
    collected = DateTimeField(default=datetime.now)

class Summary(BaseModel):
    created_at = DateTimeField(default=datetime.now)
    content = TextField(null=False)
    entry_id = ForeignKeyField(Entry)

class Feed(BaseModel):
    name = CharField(max_length=255, unique=True)
    link = TextField(unique=True)
    ping_interval = IntegerField(default=3600)
    created_at = DateTimeField(default=datetime.now)


class FeedEntries(BaseModel):
    feed_id = ForeignKeyField(Feed)
    entry_id = ForeignKeyField(Entry)


class Ping(BaseModel):
    feed = ForeignKeyField(Feed)
    timestamp = TimestampField()


db.connect()
db.create_tables([Entry, Summary, Feed, FeedEntries, Ping])