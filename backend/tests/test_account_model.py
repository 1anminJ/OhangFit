from app.models.account import Account


def test_account_table_name():
    assert Account.__tablename__ == "accounts"


def test_account_columns():
    columns = {c.name for c in Account.__table__.columns}
    assert columns == {
        "id",
        "email",
        "role",
        "password_hash",
        "access_token",
        "token_created_at",
        "converted_to_member_at",
        "created_at",
    }


def test_email_is_unique():
    assert Account.__table__.columns["email"].unique is True


def test_access_token_is_unique():
    assert Account.__table__.columns["access_token"].unique is True
