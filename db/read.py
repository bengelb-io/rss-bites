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
def get_feed_with_entries(session: Session, id: int, n: int = 10) -> tuple[Optional[Feed], Optional[List[Entry]]]:
    feed = get_feed_at_id(id)
    if not feed:
        return feed, []
    return feed, session.query(Entry).join(FeedEntries, FeedEntries.feed_id == feed.id).limit(n)

@session_provider
def get_recent_summaries(session: Session):
    return session.query(Summary).options(joinedload(Summary.entry)).limit(10).all()