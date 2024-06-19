from captcha.image import ImageCaptcha
from redis import Redis
from string import digits
from base64 import b64encode
from random import choice
from os import getenv, urandom
from flask import (
    Flask,
    session,
    render_template,
    abort,
    request,
)


class Report:
    def __init__(self):
        try:
            self.conn = Redis(host="172.30.0.30", port=6379)

        except Exception as error:
            print(error, flush=True)

    def submit(self, data: object):
        try:
            self.conn.lpush("query", data["url"])

        except Exception as error:
            print(error, flush=True)


def check_params(data):
    if not data.get("path") and not data.get("service"):
        return None

    if data.get("service") not in ["internal", "external"]:
        return None

    return {
        "service": data.get("service"),
        "path": data.get("path"),
        "captcha": data.get("captcha"),
    }


app = Flask(__name__)
report = Report()
image = ImageCaptcha(width=358, height=60)

INTERNAL_HOST = getenv("INTERNAL_HOST")
EXTERNAL_HOST = getenv("EXTERNAL_HOST")


@app.route("/", methods=["GET"])
def report_view():
    session["captcha"] = "".join(choice(digits) for _ in range(8))
    captcha = b64encode(image.generate(session["captcha"]).getvalue()).decode()
    return render_template(
        "index.html",
        captcha=captcha,
        internal=INTERNAL_HOST,
        external=EXTERNAL_HOST,
    )


@app.route("/report", methods=["GET"])
def report_handle():
    try:
        data = {
            "service": request.args.get("service"),
            "captcha": request.args.get("captcha"),
            "path": request.args.get("path"),
        }
        params = check_params(data)
        if not params:
            abort(400)

        if session["captcha"] != params["captcha"]:
            session.pop("captcha")
            abort(400)

        url = {
            "internal": INTERNAL_HOST,
            "external": EXTERNAL_HOST,
        }.get(params["service"])

        if params["path"][0] == "/":
            url += params["path"]

        else:
            url += "/" + params["path"]

        report.submit({"url": url})
        session.pop("captcha")
        return ""

    except:
        abort(400)


if __name__ == "__main__":
    app.secret_key = urandom(32)
    app.run(host="0.0.0.0", port=80, debug=False)
