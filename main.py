from flask import Flask, render_template, request
from typing import Any
from os import path, getcwd
from urllib.parse import urlparse
from db.read import get_feeds

app = Flask(__name__)


def render_page(**context: Any):
    url_object = urlparse(request.url)
    if url_object.path.endswith("/"):
        template_path = path.join("pages", *url_object.path.split("/"), "index")
    else:
        template_path = path.join("pages", *url_object.path.split("/"))
    page_path = path.join(getcwd(), "templates", template_path)
    if path.exists(page_path + ".html"):
        return render_template("main.html", page=template_path, **context)
    print("page doesn't exist at:", page_path) # Change to log
    return render_template("main.html", page=path.join("pages", "404"), request=request)

@app.get("/")
def index():
    return render_page(feeds=[{"name": "All"}])


@app.get("/feeds/")
def feeds():
    feeds = get_feeds()
    class FeedForm:
        name: str = ""
        link: str = ""
        checked: bool = False
        @classmethod
        def as_dict(cls):
            return FeedForm.__dict__

    return render_page(feeds=feeds, **dict(FeedForm.as_dict()))


@app.post("/feeds/")
def handle_form_submit():
    pass


@app.post("/feeds/ping")
def ping_feed():
    pass

if __name__ == "__main__":
    app.run(debug=True)
