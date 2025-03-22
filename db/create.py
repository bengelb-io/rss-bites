from typing import Optional
from datetime import datetime
from dateutil.parser import parse
from sqlalchemy import desc
from sqlalchemy.orm import Session
import feedparser
from db import session_provider, Feed, Entry, Ping
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
            entries=rss_entries(session, rss),
            pings=[Ping()],
        )
        session.add(feed)
        session.commit()
        return feed


def parse_rfc(date_string: str):
    date_format = "%a, %d %b %Y %H:%M:%S %Z"
    return datetime.strptime(date_string, date_format)


def rss_entries(session: Session, rss: FeedParserDict):
    assert type(rss["items"]) is list
    items = rss["items"]
    return [
        session.query(Entry).filter(Entry.guid == item["id"]).one_or_none()
        or Entry(
            title=item["title"],
            link=item["link"],
            description=item["summary"],
            published=parse(item["published"]),  # type: ignore
            guid=item["id"],
        )
        for item in items
    ]


@session_provider
def latest_ping(session: Session, feed_id: int) -> Optional[Ping]:
    return (
        session.query(Ping)
        .filter(Ping.feed_id == feed_id)
        .order_by(desc(Ping.timestamp))
        .limit(1)
        .all()[0]
    )


@session_provider
def poll_feed(session: Session, feed: Feed):
    rss = feedparser.parse(feed.link)
    valid_rss = verify_feed(rss)
    if valid_rss:
        ping = Ping(feed_id=feed.id)
        session.add_all([feed, ping, *rss_entries(session, rss)])
        session.commit()
