from app.models.payment import Payment


def test_payment_table_name():
    assert Payment.__tablename__ == "payments"


def test_payment_columns():
    columns = {c.name for c in Payment.__table__.columns}
    assert columns == {
        "id",
        "account_id",
        "profile_id",
        "amount",
        "status",
        "paid_at",
        "created_at",
    }
