from datetime import datetime, timedelta
from flask import Flask, render_template, request, make_response, Request
from db.read import get_recent_summaries, get_feeds, get_feed_with_entries
from db.create import new_feed, poll_feed, latest_ping
from db.delete import delete_feed_at_id
from db.update import edit_feed_at_id
from db import Feed

app = Flask(__name__)


def htmx_redirect(url: str):
    response = make_response("", 204)  # 204 = No Content
    response.headers["HX-Redirect"] = url
    return response


def htmx_refresh():
    response = make_response("", 204)  # 204 = No Content
    response.headers["HX-Refresh"] = "true"
    return response


state = {"visitors": 0, "recent": []}


@app.get("/")
def index():
    state["recent"] = get_recent_summaries()
    state["visitors"] += 1
    print(state["recent"])
    return render_template("base.html", page="pages/index", **state)


@app.get("/feed")
def feed():
    feeds = get_feeds()
    return render_template("base.html", page="pages/feed/index", feeds=feeds)


def poll_elapsed(request: Request, feed: Feed) -> bool:
    ping = latest_ping(feed.id)
    if not ping:
        return True
    ts: datetime = ping.timestamp  #    type: ignore
    elapsed = (request.date or datetime.now()) - ts
    print(elapsed, timedelta(minutes=feed.ttl))
    return timedelta(minutes=feed.ttl) < elapsed


@app.get("/feed/<int:id>")
def feed_at_id(id: int):
    page_arg = request.args.get("page")
    page = int(page_arg) - 1 if page_arg else 0
    feed, entries, pages = get_feed_with_entries(id, page=page)

    if not feed:
        return render_template("base.html", page="404")

    if poll_elapsed(request, feed):
        print(f"Polling feed {feed.id}")  # TODO: switch to logger
        poll_feed(feed)

    return render_template(
        "base.html",
        page="pages/feed/*",
        feed=feed,
        entries=entries,
        pages=range(1, pages + 1),
    )


@app.get("/feed/form")
def form():
    return render_template("pages/feed/form.html", error=None)


@app.post("/feed")
def create_feed():
    try:
        new_feed(request.form["link"], request.form["name"])
    except Exception as exc:
        return render_template("pages/feed/form.html", error=str(exc)), 422
    return htmx_refresh()


@app.put("/feed/<int:id>")
def edit_feed(id: int):
    edit_feed_at_id(id, request.form["name"])
    return htmx_refresh()


@app.delete("/feed/<int:id>")
def delete_feed(id: int):
    delete_feed_at_id(id)
    return htmx_redirect("/feed")
