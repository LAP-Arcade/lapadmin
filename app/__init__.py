from pathlib import Path

import flask
import werkzeug.utils
from flask import Flask

ROOT_DIR = Path(__file__).parent.resolve()
VAR_DIR = Path("var").resolve()

from app import auto_import, db  # noqa: E402


class App(Flask):
    def __init__(self):
        super().__init__(__name__)

    def redirect(self, route, external=False, code=302):
        external = external or route.split(":")[0] in ("http", "https")
        if not external and not route.startswith("/"):
            route = flask.url_for(route)
        return werkzeug.utils.redirect(route, code)

    def render(self, template_name, **context):
        default_page = template_name
        default_page = default_page.replace("/", "-")
        default_page = default_page.replace("_", "-")
        context.setdefault("page", default_page)
        return flask.render_template(f"{template_name}.html.j2", **context)

    def session(self, **kwargs):
        return db.session(**kwargs)


app = App()

auto_import.auto_import("routes")
auto_import.auto_import("cli")

if app.debug:
    VAR_DIR.mkdir(exist_ok=True)
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    db.create_all()
