from flask import Flask, render_template, request, Blueprint
from typing import Any, Optional
from os import path, getcwd
from urllib.parse import urlparse
from db.read import get_feeds
from db.create import new_feed
import feedparser

app = Flask(__name__)
# admin = Blueprint("admin", __name__, url_prefix="/admin")

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
    return render_page()


class FeedForm:
    id : Optional[int] = None
    error: Optional[str] = None

    def __init__(self, name: str = "", link = "", checked = False) -> None:
        self.name, self.link, self.checked = name, link, checked
        
    @classmethod
    def as_dict(cls):
        return FeedForm.__dict__

@app.get("/feeds/")
def feeds():
    feeds = get_feeds()


    return render_page(feeds=feeds, **FeedForm().as_dict())


@app.post("/feeds/submit")
def handle_form_submit():
    return 


@app.post("/feeds/validate")
def create_feed():
    link = request.form["link"]
    form = FeedForm(link=link)
    try:
        feed = new_feed(link)
        form.id = feed
    except Exception as e:
        form.error = str(e)
        print(form.error)
        tmpl = render_template("feed/validate.html", **form.as_dict())
        print(tmpl)
        return render_template("feed/validate.html", **form.as_dict()), 422
    return render_template("feed/validate.html", **form.as_dict()), 200


if __name__ == "__main__":
    app.run(debug=True)
