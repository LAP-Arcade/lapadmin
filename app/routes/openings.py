import typing as t

import flask
from pydantic import BaseModel, Field

from app import app
from app.db import Opening, Visit, Visitor


@app.post("/openings/<id>/delete")
def opening_delete(id):
    with app.session() as s:
        opening = s.query(Opening).get(id)
        month = opening.start.strftime("%Y-%m")
        day = opening.start.strftime("%d")
        s.delete(opening)
        s.commit()
        flask.flash(f"L'ouverture du {opening.start} a été supprimée.")
    return app.redirect("calendar_day", month=month, day=day)


class OpeningVisitorModel(BaseModel):
    visitor_id: int = Field(alias="id")
    nick: t.Optional[str]
    full_name: str


@app.post("/api/openings/<id>/visitors/")
def add_opening_visitor(id):
    with app.session() as s:
        opening = s.query(Opening).get(id)
        visitor_id = flask.request.json["visitor_id"]
        visitor = s.query(Visitor).get(visitor_id)
        s.greate(Visit, filter={"opening": opening, "visitor": visitor})
        s.commit()


@app.delete("/api/openings/<opening_id>/visitors/<visitor_id>")
def delete_visit(opening_id, visitor_id):
    with app.session() as s:
        visit = s.query(Visit).get(
            {"opening_id": opening_id, "visitor_id": visitor_id}
        )
        s.delete(visit)
        s.commit()
