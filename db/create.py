from sqlalchemy.orm import create_session
import feedparser
from db import engine, Feed, Entry, Ping
from feedparser import FeedParserDict
from datetime import datetime


def verify_feed(fpd: FeedParserDict):
    return fpd["bozo"] != 1

def new_feed(link: str):
    rss = feedparser.parse(link)
    valid_rss = verify_feed(rss)
    if valid_rss:
        with create_session(bind=engine) as session:
            feed = Feed(link=link, entries=rss_entries(rss), pings=[Ping()])
            session.add(feed)
            session.commit()
        return feed
    raise Exception("RSS could not be parsed.")


def parse_rfc(date_string: str):
    date_format = "%a, %d %b %Y %H:%M:%S %Z"
    return datetime.strptime(date_string, date_format)


def rss_entries(fpd: FeedParserDict):
    assert type(fpd["items"]) is list
    items = fpd["items"]
    return [
        Entry(
            title=item["title"],
            link=item["link"],
            description=item["summary"],
            published=parse_rfc(item["published"]),  # type: ignore
            guid=item["id"],
        )
        for item in items
    ]
