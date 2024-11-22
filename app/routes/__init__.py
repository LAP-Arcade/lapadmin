import flask
from flask_wtf import FlaskForm

from app import app


def create_delete_response(model, back, **search):
    form = FlaskForm()

    with app.session() as s:
        entity = s.query(model).filter_by(**search).first()
        if not form.validate_on_submit():
            return app.render("delete", form=form, entity=entity, back=back)
        s.delete(entity)
        s.commit()
        flask.flash(f"Entité {repr(entity)} supprimée")
    return flask.redirect(back)
