"""wait for hooks"""

from os import environ

from flask import Flask
from main import main as run_refresh

app = Flask(__name__)


@app.route("/", methods=["POST"])
def home():
    """handle post grequest"""
    run_refresh()

    return "success"


if __name__ == "__main__":
    PORT = int(environ.get("LISTEN_PORT", 8001))
    app.run(host="0.0.0.0", port=PORT)
