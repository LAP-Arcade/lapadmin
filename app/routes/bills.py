import flask

from app import app, private, sumup
from app.db import Visit
from app.db.bill import Bill


@private.get("/visits/<visit_id>/bills")
def visit_bills(visit_id):
    oldest_ref = flask.request.args.get("oldest_ref")
    newest_ref = flask.request.args.get("newest_ref")

    with app.session() as s:
        visit = s.query(Visit).filter_by(id=visit_id).first()
        visitor = visit.visitor
        opening = visit.opening
        opening_date = opening.start
        linked_refs = {b.reference for b in visit.bills}

    try:
        transactions, links = sumup.list_transactions(
            limit=20, oldest_ref=oldest_ref, newest_ref=newest_ref
        )
        if transactions and newest_ref:
            links["prev_oldest_ref"] = transactions[0].id
        if transactions and oldest_ref and "next_newest_ref" not in links:
            links["next_newest_ref"] = transactions[-1].id
        error = None
    except Exception as e:
        transactions = []
        links = {}
        error = str(e)

    return app.render(
        "bills",
        visit_id=visit_id,
        visitor=visitor,
        opening_date=opening_date,
        transactions=transactions,
        linked_refs=linked_refs,
        links=links,
        error=error,
    )


@private.post("/api/visits/<visit_id>/bills")
def link_bill(visit_id):
    data = flask.request.json
    with app.session() as s:
        visit = s.query(Visit).filter_by(id=visit_id).first()
        bill = (
            s.query(Bill)
            .filter_by(service=Bill.Service.SUMUP, reference=data["reference"])
            .first()
        )
        if not bill:
            bill = Bill(
                service=Bill.Service.SUMUP,
                reference=data["reference"],
            )
            s.add(bill)
            s.flush()
        if visit not in bill.visits:
            bill.visits.append(visit)
        s.commit()
    return "", 204


@private.delete("/api/visits/<visit_id>/bills/<reference>")
def unlink_bill(visit_id, reference):
    with app.session() as s:
        visit = s.query(Visit).filter_by(id=visit_id).first()
        bill = (
            s.query(Bill)
            .filter_by(service=Bill.Service.SUMUP, reference=reference)
            .first()
        )
        if bill and visit in bill.visits:
            bill.visits.remove(visit)
            if not bill.visits:
                s.delete(bill)
        s.commit()
    return "", 204
