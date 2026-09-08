from app.models.profile import Profile


def test_profile_table_name():
    assert Profile.__tablename__ == "profiles"


def test_profile_columns():
    columns = {c.name for c in Profile.__table__.columns}
    assert columns == {
        "id",
        "birth_date",
        "birth_time",
        "birth_time_unknown",
        "gender",
        "birth_region",
        "account_id",
        "created_at",
        "updated_at",
    }
