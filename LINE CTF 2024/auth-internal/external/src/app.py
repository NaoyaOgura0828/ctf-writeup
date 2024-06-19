import base64
from functools import wraps
import json
import os
import re
from uuid import uuid4


from flask import (
    Flask,
    request,
    session,
    redirect,
    url_for,
    abort,
    render_template,
)
import requests


app = Flask(__name__, static_url_path="/static")
app.secret_key = str(uuid4())


EXTERNAL_HOST = os.getenv("EXTERNAL_HOST")
EXTERNAL_FLAG = os.getenv("EXTERNAL_FLAG")
AUTH_USERINFO_URL = os.getenv("AUTH_USERINFO_URL")
AUTH_TOKEN_URL = os.getenv("AUTH_TOKEN_URL")
AUTH_REDIRECT_URL = os.getenv("AUTH_REDIRECT_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def escape(s):
    return re.sub(r"hx", "sanitized", s.replace(">", "&gt;").replace("<", "&lt;"), flags=re.I)


def authorized(f):
    @wraps(f)
    def check(*args, **kwargs):
        access_token = session.get("access_token")
        if access_token == None:
            return redirect(url_for("login"))

        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.get(AUTH_USERINFO_URL, headers=headers)
        if r.status_code != 200:
            session.pop("access_token", None)
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return check


@app.route("/", methods=["GET"])
@authorized
def home():
    return render_template("index.html")


@app.route("/flag", methods=["GET"])
@authorized
def flag():
    return render_template("flag.html", flag=EXTERNAL_FLAG)


@app.route("/login", methods=["GET"])
def login():
    if session.get("access_token") == None:
        return render_template("login.html", oauth_url=AUTH_REDIRECT_URL)

    return_url = escape(request.args.get("return_url", "/"))
    timeout = escape(request.args.get("timeout", "0"))
    return render_template(
        "redirect.html",
        msg=f"<meta http-equiv='refresh' content='{timeout};url={return_url}'>redirect to page in {timeout} seconds...",
    )


@app.route("/logout", methods=["GET"])
def loutout():
    if session.get("access_token") == None:
        return render_template(
            "redirect.html",
            msg='<h2 class="mb-8 mt-1 pb-1 text-3xl font-semibold">You are not logged in!</h2>',
        )

    return_url = escape(request.args.get("return_url", "/login"))
    timeout = escape(request.args.get("timeout", "3"))
    session.pop("access_token", None)
    return render_template(
        "redirect.html",
        msg=f"<meta http-equiv='refresh' content='{timeout};url={return_url}'>redirect to page in {timeout} seconds...",
    )


@app.route("/api/auth/callback", methods=["GET"])
def callback():
    code = request.args.get("code", None)
    state = request.args.get("state", None)

    if state:
        try:
            decoded_state = json.loads(base64.urlsafe_b64decode(state))
        except:
            return abort(500)

    redirect_uri = decoded_state.get("previous_uri", None)
    if not redirect_uri:
        redirect_uri = (
            EXTERNAL_HOST + "/api/auth/callback?state=eyJyZWRpcmVjdCI6Ii8ifQ=="
        )

    data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    headers = {
        "Authorization": "Basic "
        + base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode()).decode()
    }

    r = requests.post(AUTH_TOKEN_URL, headers=headers, data=data)

    if r.status_code != 200:
        return abort(400)

    session["access_token"] = r.json()["access_token"]

    if "redirect" in decoded_state.keys():
        return redirect(decoded_state["redirect"])

    return redirect(url_for("home"))


@app.route("/api/profile", methods=["GET"])
@authorized
def get_profile():
    access_token = session.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(AUTH_USERINFO_URL, headers=headers)
    if r.status_code != 200:
        abort(403)
    return r.json()


app.run(host="0.0.0.0", port=80, debug=False)
