import secrets
import urllib

import flask
import requests

from app import app
from app.db import AuthToken, Staff


@app.route("/login/")
def login():
    return app.redirect("discord_login")


def get_authorization_url(state: str = None):
    url = "https://discord.com/oauth2/authorize"
    redirect = app.url_for("discord_callback", _external=True)
    params = {
        "state": state,
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": "identify",
        "client_id": app.config["DISCORD_CLIENT_ID"],
    }
    return f"{url}?" + urllib.parse.urlencode(params)


@app.route("/login/discord/")
def discord_login():
    url = get_authorization_url()
    return app.redirect(url)


@app.route("/login/discord/callback")
def discord_callback():
    response = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "code": flask.request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": app.url_for("discord_callback", _external=True),
        },
        auth=(
            app.config["DISCORD_CLIENT_ID"],
            app.config["DISCORD_CLIENT_SECRET"],
        ),
    )
    response.raise_for_status()
    data = response.json()

    response = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    response.raise_for_status()
    data = response.json()

    with app.session() as s:
        staff = s.query(Staff).filter_by(discord_id=data["id"]).first()
        if not staff:
            raise ValueError("Discord user is not a staff member")
        token = AuthToken(staff=staff)
        s.add(token)
        s.commit()
        cookie = token.cookie
    redirect = app.redirect("private.index")
    redirect.set_cookie("auth", cookie)
    return redirect
