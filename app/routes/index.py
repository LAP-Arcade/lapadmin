from app import app


@app.get("/")
def index():
    return app.redirect("calendar_redirect")
