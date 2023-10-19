from flask import Flask
from storage_hooks import AWSHook

app = Flask(__name__)


@app.route("/api/receipt/upload", method=["POST"])
def upload_receipt():
    return 404


@app.route("/api/receipt/view")
def view_receipt():
    return 404
