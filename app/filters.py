from datetime import datetime

from arrow import Arrow

from app import app


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
