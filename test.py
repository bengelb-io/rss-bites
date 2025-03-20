import json
import feedparser
rss = feedparser.parse("https://www.sciencedaily.com/rss/all.xml")
open("rss.json", "x").write(json.dumps(rss.get("items")))