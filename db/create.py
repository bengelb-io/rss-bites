from typing import Optional
from datetime import datetime
from dateutil.parser import parse
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, all_, select
import feedparser
from db import session_provider, Feed, Entry, Ping, FeedEntries
from feedparser import FeedParserDict


def verify_feed(fpd: FeedParserDict):
    return fpd["bozo"] != 1


@session_provider
def new_feed(session: Session, link: str, name: str):
    rss = feedparser.parse(link)
    valid_rss = verify_feed(rss)
    if valid_rss:
        ttl = rss["channel"]["ttl"]
        feed = Feed(
            name=name,
            link=link,
            ttl=ttl if ttl else 60,
            pings=[Ping()],
        )
        session.add_all([feed, *rss_entries(session, rss, feed)])
        session.commit()
        return feed


def parse_rfc(date_string: str):
    date_format = "%a, %d %b %Y %H:%M:%S %Z"
    return datetime.strptime(date_string, date_format)


def rss_entries(session: Session, rss: FeedParserDict, feed: Feed):
    assert type(rss["items"]) is list
    items: list = rss["items"]
    guids = [item["id"] for item in items]
    recorded_guids = [
        entry.guid for entry in session.query(Entry).join(Entry.feeds).filter(Entry.guid.in_(guids)).all()
    ]  # Already recorded entries in different feeds.

    new_entries = [
        Entry(
            title=item["title"],
            link=item["link"],
            description=item["summary"],
            published=parse(item["published"]),  # type: ignore
            guid=item["id"],
            feeds=[feed]
        )
        for item in filter(lambda item: item["id"] not in recorded_guids, items)
    ]
    entries_from_another_mother = select(FeedEntries.entry_id).filter(FeedEntries.feed_id == feed.id).scalar_subquery()
    updated_entries =  session.query(Entry).filter(Entry.guid.in_(guids), Entry.id.not_in(entries_from_another_mother)).all()
    print("updated entries:", len(updated_entries))
    for entry in updated_entries:
        entry.feeds.append(feed)
    return [*new_entries, *updated_entries]


@session_provider
def latest_ping(session: Session, feed_id: int) -> Optional[Ping]:
    return (
        session.query(Ping)
        .filter(Ping.feed_id == feed_id)
        .order_by(desc(Ping.timestamp))
        .one_or_none()
    )

@session_provider
def ttl(session: Session, ping: Ping) -> int:
    return session.query(Feed.ttl).filter(Feed.id == ping.feed_id).scalar()

def poll_feed(session: Session, feed_id: int) -> Ping:
    ping = None

    feed = session.query(Feed).filter(Feed.id == feed_id).one_or_none()
    if not feed:
        raise Exception("Feed doesn't exist.")
    
    rss = feedparser.parse(feed.link)
    valid_rss = verify_feed(rss)    
    if valid_rss:
        ping = Ping(feed_id=feed.id)
        entries = rss_entries(session, rss, feed)
        session.add_all([feed, *entries, ping])
        session.commit()

    return ping
