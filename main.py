from flask import Flask, render_template
from config import load_config, RSSConfig

app = Flask(__name__)
rss_config: RSSConfig = load_config()


@app.get("/")
def index():
    return render_template("index.html", feeds=rss_config.feeds)


if __name__ == "__main__":
    app.run(debug=True)
