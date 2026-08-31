import datetime

import flask

from app import app, private, routes
from app.db import Availability


@private.post("/api/availability/<date>/")
def set_availability(date):
    print(date)
    date = datetime.date.fromisoformat(date)
    with app.session() as s:
        staff_id = flask.request.user.id
        availability_type = flask.request.json["type"]
        action = s.greate(
            Availability, filter={"staff_id": staff_id, "date": date}
        )
        if not availability_type:
            s.delete(action.instance)
        else:
            action.instance.type = availability_type
        s.commit()
    return "", 204
