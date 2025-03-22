from os import path, getcwd
from typing import Any
from urllib.parse import urlparse
from flask import render_template, request

page_template_name = "index"

def render_page(**context: Any):
    """Renders template path in template/pages/ directory."""
    url_object = urlparse(request.url)
    if url_object.path.endswith("/"):
        template_path = path.join("pages", *url_object.path.split("/"), page_template_name)
    else:
        template_path = path.join("pages", *url_object.path.split("/"))
    print(template_path)
    page_path = path.join(getcwd(), "templates", template_path)
    if path.exists(page_path + ".html"):
        return render_template("base.html", page=template_path, **context)
    print("page doesn't exist at:", page_path + ".html") # Change to log
    return render_template("base.html", page=path.join("pages", "404"), request=request)
