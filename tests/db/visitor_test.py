from datetime import datetime

from app.db.visitor import Visitor


def test_given_no_deleted_at_when_checking_is_deleted_then_returns_false():
    assert Visitor(deleted_at=None).is_deleted is False


def test_given_a_deleted_at_when_checking_is_deleted_then_returns_true():
    assert Visitor(deleted_at=datetime(2026, 1, 1, 12, 0)).is_deleted is True


def test_given_a_deleted_visitor_with_missing_fields_when_checking_is_incomplete_then_returns_false():
    visitor = Visitor()
    visitor.first_name = ""
    visitor.last_name = ""
    visitor.email = ""
    visitor.deleted_at = datetime(2026, 1, 1, 12, 0)
    assert visitor.is_incomplete is False
