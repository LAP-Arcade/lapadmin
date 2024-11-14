from app import app, private


@private.get("/")
def index():
    return app.redirect(".calendar_redirect")
