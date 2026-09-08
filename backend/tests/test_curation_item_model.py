from app.models.curation_item import CurationItem


def test_curation_item_table_name():
    assert CurationItem.__tablename__ == "curation_items"


def test_curation_item_columns():
    columns = {c.name for c in CurationItem.__table__.columns}
    assert columns == {"id", "element", "name", "category", "image_url", "created_at"}
