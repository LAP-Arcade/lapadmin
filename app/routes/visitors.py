from datetime import UTC, date, datetime
from uuid import uuid4

import flask
from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, StringField
from wtforms.validators import DataRequired

from app import app, private
from app.db import Visitor


@private.get("/visitors/")
def visitors():
    with app.session() as s:
        visitors = s.query(Visitor).filter(~Visitor.is_deleted).all()
        visitors.sort(key=lambda x: (x.nick or x.full_name).lower())
        return app.render("visitors", visitors=visitors)


class VisitorEditForm(FlaskForm):
    first_name = StringField("Prénom")
    last_name = StringField("Nom de famille")
    email = EmailField("Email")
    nick = StringField("Surnom")
    is_member = BooleanField("Adhérent")


@private.route("/visitors/<int:id>/")
def visitor_edit(id):
    with app.session() as s:
        visitor = s.query(Visitor).filter_by(id=id).first()
    if not visitor or visitor.is_deleted:
        flask.abort(404)

    form = VisitorEditForm()
    form.process(flask.request.form, obj=visitor)

    if not form.validate_on_submit():
        return app.render(
            "visitor_edit",
            form=form,
            visitor=visitor,
            self_edit_link_form=FlaskForm(),
        )

    with app.session() as s:
        visitor.first_name = form.first_name.data
        visitor.last_name = form.last_name.data
        visitor.email = form.email.data
        visitor.nick = form.nick.data
        if form.is_member.data:
            visitor.mark_as_member()
        s.add(visitor)
        s.commit()
        flask.flash(f"Profil du visiteur {visitor} enregistré")

    return flask.redirect(".visitors")


@private.post("/visitors/<int:id>/edit/")
def visitor_self_edit_generate(id):
    form = FlaskForm()
    with app.session() as s:
        visitor = s.query(Visitor).filter_by(id=id).first()
        if not visitor or visitor.is_deleted:
            flask.abort(404)
        if not form.validate_on_submit():
            flask.abort(400)
        visitor.self_edit_uuid = str(uuid4())
        s.add(visitor)
        s.commit()
        flask.flash("Lien d'édition à usage unique généré")
    return flask.redirect(flask.url_for(".visitor_edit", id=id))


@private.post("/visitors/<int:id>/edit/delete/")
def visitor_self_edit_link_delete(id):
    form = FlaskForm()
    with app.session() as s:
        visitor = s.query(Visitor).filter_by(id=id).first()
        if not visitor or visitor.is_deleted:
            flask.abort(404)
        if not form.validate_on_submit():
            flask.abort(400)
        visitor.self_edit_uuid = None
        s.add(visitor)
        s.commit()
        flask.flash("Lien d'édition à usage unique supprimé")
    return flask.redirect(flask.url_for(".visitor_edit", id=id))


@private.route("/visitors/<int:id>/delete/")
def visitor_delete(id):
    # We don't actually delete the entry: we anonymize it to be able to keep the history of openings/visits.
    form = FlaskForm()
    back = flask.url_for(".visitors")
    with app.session() as s:
        visitor = s.query(Visitor).filter_by(id=id).first()
        if not visitor or visitor.is_deleted:
            flask.abort(404)
        if not form.validate_on_submit():
            return app.render("delete", form=form, entity=visitor, back=back)
        old_visitor = repr(visitor)
        visitor.first_name = None
        visitor.last_name = None
        visitor.nick = None
        visitor.email = None
        visitor.deleted_at = datetime.now(UTC)
        s.add(visitor)
        s.commit()
        flask.flash(f"Entité {old_visitor} supprimée")
    return flask.redirect(back)


@private.route("/visitors/new/")
def visitor_new():
    form = VisitorEditForm()

    if not form.validate_on_submit():
        return app.render("visitor_edit", form=form, title="Nouveau visiteur")

    with app.session() as s:
        visitor = Visitor()
        visitor.first_name = form.first_name.data
        visitor.last_name = form.last_name.data
        visitor.email = form.email.data
        visitor.nick = form.nick.data
        if form.is_member.data:
            visitor.member_since = date.today()
        if not (visitor.full_name or visitor.nick):
            flask.flash("Impossible de créer un visiteur sans nom")
            return app.render("visitor_edit", form=form)
        s.add(visitor)
        s.commit()
        flask.flash(f"Profil du visiteur {visitor} enregistré")

    return flask.redirect(".visitors")


class VisitorSelfEditForm(FlaskForm):
    first_name = StringField("Prénom", validators=[DataRequired()])
    last_name = StringField("Nom de famille", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    nick = StringField("Surnom")
    accept_rules = BooleanField(validators=[DataRequired()])


# Not registered on the `private` blueprint: this page must be reachable
# without being logged in, using its single-use uuid as the only credential.
@app.route("/members/form/<uuid>/")
def visitor_self_edit(uuid):
    with app.session() as s:
        visitor = s.query(Visitor).filter_by(self_edit_uuid=uuid).first()
    if not visitor or visitor.is_deleted:
        flask.abort(404)

    form = VisitorSelfEditForm()
    form.process(flask.request.form, obj=visitor)
    was_member = visitor.is_member
    if was_member:
        form.accept_rules.validators = []

    if not form.validate_on_submit():
        return app.render("visitor_self_edit", form=form, visitor=visitor)

    with app.session() as s:
        visitor.first_name = form.first_name.data
        visitor.last_name = form.last_name.data
        visitor.email = form.email.data
        visitor.nick = form.nick.data
        visitor.self_edit_uuid = None
        if not was_member:
            visitor.mark_as_member()
        s.add(visitor)
        s.commit()

        return app.render("visitor_self_edit", visitor=visitor, saved=True)


@app.route("/members/form/<uuid>/qr")
def visitor_self_edit_qr(uuid):
    with app.session() as s:
        visitor = s.query(Visitor).filter_by(self_edit_uuid=uuid).first()
    if not visitor or visitor.is_deleted:
        flask.abort(404)

    self_edit_url = flask.url_for(
        "visitor_self_edit", uuid=uuid, _external=True
    )
    return app.render("visitor_self_edit_qr", self_edit_url=self_edit_url)
