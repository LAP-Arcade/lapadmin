from flask import request

from app import app, private
from app.db import AuthToken


@private.before_request
def check_login():
    cookie = request.cookies.get("auth")
    redirect = app.redirect("login")
    request.user = None
    if not cookie:
        return redirect
    with app.session() as session:
        token = AuthToken.validate(session, cookie)
        if not token:
            return redirect
        user = token.staff
    request.user = user
