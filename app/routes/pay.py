from flask_wtf import FlaskForm

from app import app, items, private
from app.db import visitor


class PayForm(FlaskForm):
    pass


@private.get("/pay/")
def pay():
    # TODO
    form = PayForm()
    return app.render(
        "pay",
        visitors=visitor.get_input_list(),
        items=items.get_all(),
        form=form,
    )
