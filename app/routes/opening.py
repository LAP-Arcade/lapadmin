import flask

from app import app


@app.get("/openings/")
def create_opening():
    return app.render("opening_create")


@app.post("/openings/")
def create_opening_post():
    return str(flask.request.form)


@app.get("/openings/<int:opening_id>/")
def opening(opening_id: int):
    return f"Read opening {opening_id}"
