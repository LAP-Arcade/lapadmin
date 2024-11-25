import secrets
from pathlib import Path

import flask
import werkzeug.utils
from arrow import Arrow
from flask import Blueprint, Flask
from flask.sansio.scaffold import Scaffold
from pydantic import BaseModel

# These need to be defined before importing other modules otherwise they'll
# cause circular imports.
ROOT_DIR = Path(__file__).parent.resolve()
VAR_DIR = Path("var").resolve()
DATA_DIR = Path("data").resolve()

from app import auto_import, db  # noqa: E402
from app.config import Config  # noqa: E402


class App(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.g = {}
        self.config.from_object(Config())

        @self.context_processor
        def _():
            return {
                "now": Arrow.now(),
            }

        secret_key_path = VAR_DIR / "secret_key.txt"
        if not secret_key_path.exists():
            secret_key_path.parent.mkdir(exist_ok=True, parents=True)
            secret_key_path.write_text(secrets.token_hex())
        self.config["SECRET_KEY"] = secret_key_path.read_text().strip()

    def redirect(self, route, external=False, code=302, **kwargs):
        external = external or route.split(":")[0] in ("http", "https")
        if not external and not route.startswith("/"):
            route = flask.url_for(route, **kwargs)
        return werkzeug.utils.redirect(route, code)

    def render(self, template_name, **context):
        default_page = template_name
        default_page = default_page.replace("/", "-")
        default_page = default_page.replace("_", "-")
        context.setdefault("page", default_page)
        return flask.render_template(f"{template_name}.html.j2", **context)

    def route(self, rule, **options):
        """
        Using @app.route instead of @app.<method> defaults to accepting both GET
        and POST methods, useful for form-based routes.
        """
        options.setdefault("methods", ("GET", "POST"))
        # We can't use super() here because it will fail if we use this method
        # from a Blueprint. Resolving the class here allows us to call this
        # method from both the App and Blueprint classes.
        return Scaffold.route(self, rule, **options)

    def session(self, **kwargs):
        return db.session(**kwargs)

    def make_response(self, return_value):
        if isinstance(return_value, BaseModel):
            return_value: BaseModel = return_value
            return flask.jsonify(return_value.model_dump())
        if return_value is None:
            return flask.Response(status=204)
        return super().make_response(return_value)


class Blueprint(Blueprint):
    def route(self, *args, **kwargs):
        return App.route(self, *args, **kwargs)


app = App()
private = Blueprint("private", __name__)

auto_import.auto_import("routes")
auto_import.auto_import("cli")
auto_import.auto_import("filters")

app.register_blueprint(private)


def create_app(debug=False):
    app.debug = app.debug or debug

    if app.debug:
        VAR_DIR.mkdir(exist_ok=True)
        app.config["TEMPLATES_AUTO_RELOAD"] = True

        db.create_all()

    from app import staffs

    staffs.reset()

    return app
