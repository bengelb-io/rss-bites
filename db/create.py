from config import RSSConfig

from db import Feed

def get_feeds(rss_config: RSSConfig) -> list[Feed]:
    return [
        Feed.get_or_create(
            name=feed.name,
            link=feed.name,
        )
        for feed in rss_config.feeds
    ]
