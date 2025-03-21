from typing import Optional
from flask import Flask, render_template, request, make_response
from db.read import get_recent_summaries, get_feeds, get_feed_with_entries
from db.create import new_feed
from db.delete import delete_feed_at_id
from db.update import edit_feed_at_id
from db import Feed

app = Flask(__name__)

def htmx_redirect(url: str):
    response = make_response('', 204)  # 204 = No Content
    response.headers['HX-Redirect'] = url
    return response

def htmx_refresh():
    response = make_response('', 204)  # 204 = No Content
    response.headers['HX-Refresh'] = 'true'
    return response   

state = {
    "visitors": 0,
    "recent": [] 
}

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

@app.get("/feed/<int:id>")
def feed_at_id(id: int):
    feed, entries = get_feed_with_entries(id)
    if not feed:
        return render_template("base.html", page="404")
    return render_template("base.html", page="pages/feed/*", feed=feed, entries=entries)