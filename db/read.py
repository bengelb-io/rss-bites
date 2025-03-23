from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from db import session_provider, Feed, Entry, Summary, FeedEntries


@session_provider
def get_feeds(session: Session) -> List[Feed]:
    return session.query(Feed).all()


@session_provider
def get_feed_at_id(session: Session, id: int):
    return session.query(Feed).filter(Feed.id == id).one_or_none()


@session_provider
def get_feed_with_entries(
    session: Session, id: int, page: int = 0, n: int = 10
) -> tuple[Optional[Feed], Optional[List[Entry]], int]:
    feed = get_feed_at_id(id)
    offset = page * n
    if not feed:
        return feed, [], 0
    pages = (
        session.query(Entry).join(Entry.feeds).filter(Feed.id == feed.id).count() // n
    )
    entries = (
        session.query(Entry)
        .join(FeedEntries, FeedEntries.feed_id == feed.id)
        .offset(offset)
        .limit(n)
        .all()
    )
    return feed, entries, pages


@session_provider
def get_recent_summaries(session: Session):
    return session.query(Summary).options(joinedload(Summary.entry)).limit(10).all()

@session_provider
def get_entry_at_id(session: Session, id: int):
    return session.query(Entry).options(joinedload(Entry.summaries), joinedload(Entry.feeds)).filter(Entry.id == id).one_or_none()


def paginated_feed_at_id(session: Session, id: int, page: int, n: int = 10) -> tuple[Optional[Feed], list[Entry]]:
    offset = page * n
    feed = (
        session.query(Feed)
        .filter(Feed.id == id)
        .one_or_none()
    )
    if not feed:
        return None, []
    entries = (
        session.query(Entry)
        .join(FeedEntries, FeedEntries.entry_id == Entry.id)
        .filter(FeedEntries.feed_id == feed.id)
        .offset(offset)
        .limit(n)
        .all()
    )
    return feed, entries

def total_entries_in_feed(session: Session, feed: Feed):
    return session.query(Entry).join(Entry.feeds).filter(Feed.id == feed.id).count()