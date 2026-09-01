from dataclasses import dataclass
from datetime import datetime

import flask
from arrow import Arrow

from app import app, private
from app.db import Availability, Opening


def get_calendar_start(month: Arrow) -> Arrow:
    return month.floor("week")


def get_calendar_end(month: Arrow) -> Arrow:
    return get_calendar_start(month).shift(weeks=6)


@dataclass
class Day:
    date: Arrow
    openings: list[Opening]
    availabilities: list[Availability]
    me: Availability.Type | None = None

    @property
    def is_today(self):
        return self.date.date() == Arrow.now().date()

    @property
    def is_weekend(self):
        return self.date.weekday() >= 5

    @property
    def is_past(self):
        return self.date < Arrow.fromdate(Arrow.now().date())

    def __str__(self):
        return self.date.format("D")


@private.get("/calendar/")
def calendar_redirect():
    today = Arrow.now()
    month = today.format("YYYY-MM")
    return app.redirect(".calendar_month", month=month)


@private.get("/calendar/<month>/")
def calendar_month(month):
    date = Arrow.fromdate(datetime.strptime(month, "%Y-%m"))
    previous = date.shift(months=-1).format("YYYY-MM")
    next = date.shift(months=1).format("YYYY-MM")
    start = get_calendar_start(date)
    end = get_calendar_end(date)
    with app.session() as s:
        openings = (
            s.query(Opening)
            .filter(
                Opening.start >= start.datetime, Opening.start < end.datetime
            )
            .all()
        )

    openings_by_day = {}
    for opening in openings:
        for i in range((opening.end.date() - opening.start.date()).days + 1):
            day = Arrow.fromdate(opening.start).shift(days=i).format("MMDD")
            openings_by_day.setdefault(day, [])
            openings_by_day[day].append(opening)

    availabilities_by_day = {}
    with app.session() as s:
        availabilities = (
            s.query(Availability)
            .filter(
                Availability.date >= start.date(),
                Availability.date < end.date(),
            )
            .all()
        )
    for availability in availabilities:
        day = Arrow.fromdate(availability.date).format("MMDD")
        availabilities_by_day.setdefault(day, [])
        availabilities_by_day[day].append(availability)

    days = []
    for i in range((end - start).days):
        day = start.shift(days=i)
        availabilities = availabilities_by_day.get(day.format("MMDD"), [])
        me = None
        for availability in availabilities:
            if availability.staff_id == flask.request.user.id:
                me = availability.type
                break
        days.append(
            Day(
                date=day,
                openings=openings_by_day.get(day.format("MMDD"), []),
                availabilities=availabilities,
                me=me,
            )
        )

    return app.render(
        "calendar",
        days=days,
        previous=previous,
        next=next,
        date=date,
        month=month,
        Availability=Availability,
    )
