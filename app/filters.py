from datetime import datetime, timedelta

from arrow import Arrow

from app import app


@app.template_filter("format_duration")
def format_duration(td: timedelta) -> str:
    total_minutes = int(td.total_seconds() / 60)
    hours = total_minutes // 60
    mins = total_minutes % 60
    if hours > 0:
        return f"{hours}h{mins:02d}" if mins else f"{hours}h"
    return f"{mins}min"


@app.add_template_filter
def arrow(value, func="humanize", arg=None) -> str:
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
        obj = Arrow.fromdatetime(value)
    elif isinstance(value, datetime):
        obj = Arrow.fromdatetime(value)
    elif isinstance(value, Arrow):
        obj = value
    else:
        raise ValueError(f"Unsupported type: {type(value)} for {value}")
    f = getattr(obj, func)
    if arg:
        return f(arg)
    return f()


@app.template_filter("repr")
def repr_(value) -> str:
    return repr(value)
