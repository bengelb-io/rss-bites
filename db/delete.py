from sqlalchemy.orm import Session
from db import session_provider, Feed, FeedEntries

@session_provider
def delete_feed_at_id(session: Session, id: int):
    session.query(Feed).filter(Feed.id == id).delete()
    session.query(FeedEntries).filter(FeedEntries.feed_id == id).delete()
    session.commit()