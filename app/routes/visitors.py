import flask
from flask_wtf import FlaskForm
from wtforms import EmailField, StringField

from app import app
from app.db import Visitor


@app.get("/visitors/")
def visitors():
    with app.session() as s:
        visitors = s.query(Visitor).all()
        visitors.sort(key=lambda x: (x.nick or x.full_name).lower())
        return app.render("visitors", visitors=visitors)


class VisitorEditForm(FlaskForm):
    first_name = StringField("Prénom")
    last_name = StringField("Nom de famille")
    email = EmailField("Email")
    nick = StringField("Surnom")


@app.route("/visitors/<int:id>/")
def visitor_edit(id):
    with app.session() as s:
        visitor = s.query(Visitor).filter_by(id=id).first()
    if not visitor:
        flask.abort(404)

    form = VisitorEditForm()
    form.process(flask.request.form, obj=visitor)

    if not form.validate_on_submit():
        return app.render("visitor_edit", form=form, visitor=visitor)

    with app.session() as s:
        visitor.first_name = form.first_name.data
        visitor.last_name = form.last_name.data
        visitor.email = form.email.data
        visitor.nick = form.nick.data
        s.commit()
        flask.flash(f"Profil du visiteur {visitor} enregistré")

    return flask.redirect("visitors")


@app.route("/visitors/new/")
def visitor_new():
    form = VisitorEditForm()

    if not form.validate_on_submit():
        return app.render("visitor_edit", form=form)

    with app.session() as s:
        visitor = Visitor()
        visitor.first_name = form.first_name.data
        visitor.last_name = form.last_name.data
        visitor.email = form.email.data
        visitor.nick = form.nick.data
        if not (visitor.full_name or visitor.nick):
            flask.flash("Impossible de créer un visiteur sans nom")
            return app.render("visitor_edit", form=form)
        s.add(visitor)
        s.commit()
        flask.flash(f"Profil du visiteur {visitor} enregistré")

    return flask.redirect("visitors")
