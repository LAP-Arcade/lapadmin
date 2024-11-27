import flask
from flask_wtf import FlaskForm
from wtforms.fields import SelectField, StringField
from wtforms.validators import DataRequired

from app import app, items, private
from app.db import Payment, visitor


class PayForm(FlaskForm):
    amount = StringField(validators=[DataRequired()])
    method = SelectField(
        choices=[(x.name, x.value) for x in Payment.Method],
        default=Payment.Method.CARD.name,
    )
    notes = StringField()


@private.get("/pay/")
def pay():
    form = PayForm()
    return app.render(
        "pay",
        visitors=visitor.get_input_list(),
        items=items.get_input_list(),
        form=form,
    )
