from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from typing import Any, Callable, TypeVar, Protocol, Generic
from sqlalchemy.orm import Session, create_session
from functools import wraps

# Create engine and base
engine = create_engine("sqlite:///bite.db")
Base = declarative_base()


class Entry(Base):
    __tablename__ = "entry"

    id = Column(Integer, primary_key=True)

    # RSS Fields
    title = Column(String(255))
    link = Column(Text)
    description = Column(Text)
    published = Column(DateTime)
    guid = Column(Text, unique=True, index=True)

    # Metadata
    collected = Column(DateTime, default=datetime.now)

    # Relationships
    summaries = relationship("Summary", back_populates="entry")
    feeds = relationship(
        "Feed",
        secondary="feed_entries",
        back_populates="entries",
    )


class Summary(Base):
    __tablename__ = "summary"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    content = Column(Text, nullable=False)
    entry_id = Column(Integer, ForeignKey("entry.id"))

    # Relationship
    entry = relationship("Entry", back_populates="summaries")


class Feed(Base):
    __tablename__ = "feed"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    link = Column(Text, unique=True)
    ttl = Column(Integer, default=60)  # In minutes
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    entries = relationship(
        "Entry",
        secondary="feed_entries",
        back_populates="feeds",
    )
    pings = relationship("Ping", back_populates="feed")


class FeedEntries(Base):
    __tablename__ = "feed_entries"

    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey("feed.id"))
    entry_id = Column(Integer, ForeignKey("entry.id"))

    # We can add a unique constraint to prevent duplicates
    __table_args__ = (UniqueConstraint("feed_id", "entry_id", name="_feed_entry_uc"),)


class Ping(Base):
    __tablename__ = "ping"

    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey("feed.id"))
    timestamp = Column(DateTime, default=datetime.now)

    # Relationship
    feed = relationship("Feed", back_populates="pings")


# Create all tables
Base.metadata.create_all(engine)


T = TypeVar("T", covariant=True)


class SessionReciever(Protocol, Generic[T]):
    def __call__(self, session: Session, *args, **kwds: Any) -> T: ...


def session_provider(func: SessionReciever[T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs):
        with create_session(bind=engine) as session:
            return func(session, *args, **kwargs)

    return wrapper
