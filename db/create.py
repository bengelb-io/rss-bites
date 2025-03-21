from sqlalchemy.orm import create_session, Session
import feedparser
from db import engine, session_provider, Feed, Entry, Ping
from feedparser import FeedParserDict
from datetime import datetime
from dateutil.parser import parse


def verify_feed(fpd: FeedParserDict):
    return fpd["bozo"] != 1


@session_provider
def new_feed(session: Session, link: str, name: str):
    rss = feedparser.parse(link)
    valid_rss = verify_feed(rss)
    if valid_rss:
        ttl = rss["channel"]["ttl"]
        feed = Feed(name=name, link=link, ttl=ttl if ttl else 60, entries=rss_entries(session, rss), pings=[Ping()])
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
