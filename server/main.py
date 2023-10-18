from flask import Flask
from storage_hooks import AWSHook

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello World!</p>"
