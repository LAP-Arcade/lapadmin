from dataclasses import dataclass

import flask
from flask_wtf import FlaskForm
from wtforms.fields import SelectField, StringField
from wtforms.validators import DataRequired

from app import app, items, private
from app.db import Payment, Visit, Visitor, visitor


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
    visitor_id, opening_id = flask.request.args.get(
        "visitor"
    ), flask.request.args.get("opening")
    if visitor_id and opening_id:
        with app.session() as s:
            visit = s.query(Visit).get((visitor_id, opening_id))
    else:
        visit = None
    return app.render(
        "pay",
        visitors=visitor.get_input_list(),
        items=items.get_input_list(),
        form=form,
        visit=visit,
    )


@dataclass
class PayAPIResponse:
    price: float
    discount: str


@private.get("/api/pay/")
def get_price():
    item_name = flask.request.args.get("item")
    duration = flask.request.args.get("duration")
    visitor_id = flask.request.args.get("visitor")
    if not (item := items.get_by_string(item_name)):
        return {"error": "Item not found"}, 404
    discount = None
    if visitor_id:
        with app.session() as s:
            visitor = s.query(Visitor).get(visitor_id)
            # TODO
            # for d in visitor.discounts:
            #     if d.item == item.id:
            #         discount = d
            #         break
    if discount:
        pass
        # TODO
    price = item.price
    if (
        item.type == items.ItemEntry.Type.ENTRY
        and item.billing == items.ItemEntry.Billing.HOURLY
    ):
        duration = duration.replace(":", "h")
        if duration.isdigit():
            duration += "h"
        if duration.endswith("m"):
            duration = duration[:-1]
        if duration.endswith("h"):
            duration += "00"
        if duration.endswith("min"):
            duration = duration[:-3]
        hours, minutes = duration.split("h")
        hours = hours or 0
        minutes = minutes or 0
        hours, minutes = int(hours), int(minutes)
        if minutes > 40:
            minutes = 60
        elif minutes > 10:
            minutes = 30
        half_hours = int(hours * 2 + (minutes / 30))
        price = (item.price * half_hours) / 2
        if item.max and price > item.max:
            price = item.max
    return PayAPIResponse(price=price, discount=discount)
