from sqlalchemy.orm import Session
from db import session_provider, Feed


@session_provider
def edit_feed_at_id(session: Session, id: int, name: str):
    feed = session.query(Feed).filter(Feed.id == id).one_or_none()
    if not feed:
        raise Exception("Feed not found.")
    feed.name = name
    session.commit()
