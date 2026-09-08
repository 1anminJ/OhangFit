from app.models.color_mapping import ColorMapping


def test_color_mapping_table_name():
    assert ColorMapping.__tablename__ == "color_mappings"


def test_color_mapping_columns():
    columns = {c.name for c in ColorMapping.__table__.columns}
    assert columns == {"id", "element", "color_name", "hex_code", "created_at"}
