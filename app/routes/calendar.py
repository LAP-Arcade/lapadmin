from dataclasses import dataclass
from datetime import datetime

import flask
from arrow import Arrow

from app import app
from app.db import Opening


def get_calendar_start(month: Arrow) -> Arrow:
    return month.floor("week")


def get_calendar_end(month: Arrow) -> Arrow:
    return get_calendar_start(month).shift(weeks=6)


@dataclass
class Day:
    date: Arrow
    opening: Opening = None

    @property
    def is_today(self):
        return self.date.date() == Arrow.now().date()

    @property
    def is_weekend(self):
        return self.date.weekday() >= 5

    @property
    def is_past(self):
        return self.date < Arrow.now()

    def __str__(self):
        return self.date.format("YYYY-MM-DD")


@app.get("/calendar/")
def calendar():
    month = flask.request.args.get("month")
    if not month:
        today = Arrow.now()
        month = today.format("YYYY-MM")
        redirect = app.redirect("calendar", code=303)
        redirect.headers["Location"] += f"?month={month}"
        return redirect

    month = Arrow.fromdate(datetime.strptime(month, "%Y-%m"))
    previous = month.shift(months=-1).format("YYYY-MM")
    next = month.shift(months=1).format("YYYY-MM")
    start = get_calendar_start(month)
    end = get_calendar_end(month)
    with app.session() as s:
        openings = s.query(Opening).filter(
            Opening.start >= start.datetime, Opening.start < end.datetime
        )
    openings_by_iso = {
        opening.start.date().isoformat(): opening for opening in openings
    }
    days = []
    for i in range((end - start).days):
        day = start.shift(days=i)
        days.append(
            Day(date=day, opening=openings_by_iso.get(day.date().isoformat()))
        )
    return app.render(
        "calendar", days=days, previous=previous, next=next, month=month
    )
