from yaml import safe_load
from os import getcwd
from os.path import join


class Feed:
    link: str
    name: str

    def __init__(self, **kwargs):
        self.link = kwargs["link"]
        self.name = kwargs["name"]


class RSSConfig:
    feeds: list[Feed]

    def __init__(self, feeds: list):
        self.feeds = feeds


def load_config() -> RSSConfig:
    config_path = join(getcwd(), "config.yml")
    # stat(config_path)

    config_dict = safe_load(open(config_path))
    assert type(config_dict) is dict
    rss: list[dict] = config_dict["rss"]
    return RSSConfig([Feed(**feed) for feed in rss])
