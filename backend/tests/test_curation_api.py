import uuid

from app.models.color_mapping import ColorMapping
from app.models.curation_item import CurationItem


def _create_profile(client, **overrides):
    # 1990-05-20 / 10:30:00 은 MockSajuAdapter로 항상 missing_elements=["금"]을 낸다
    # (backend/app/adapters/saju.py의 결정론적 해시 기준, test_saju_adapter.py와 별개로 확인됨).
    body = {
        "birth_date": "1990-05-20",
        "birth_time": "10:30:00",
        "birth_time_unknown": False,
        "gender": "female",
        "birth_region": "서울",
    }
    body.update(overrides)
    res = client.post("/profiles", json=body)
    return res.json()["id"]


def _seed_curation_data(db_session):
    db_session.add_all(
        [
            ColorMapping(element="금", color_name="흰색", hex_code="#FFFFFF"),
            ColorMapping(element="금", color_name="은색", hex_code="#C0C0C0"),
            ColorMapping(element="화", color_name="빨강", hex_code="#DC143C"),
            CurationItem(
                element="금", name="화이트 셔츠", category="아우터", image_url="https://example.com/1.jpg"
            ),
            CurationItem(
                element="화", name="빨강 스카프", category="액세서리", image_url="https://example.com/2.jpg"
            ),
        ]
    )
    db_session.commit()


def test_curation_requires_analysis_first(client):
    profile_id = _create_profile(client)
    response = client.get(f"/profiles/{profile_id}/curation")
    assert response.status_code == 404


def test_curation_profile_not_found(client):
    response = client.get(f"/profiles/{uuid.uuid4()}/curation")
    assert response.status_code == 404


def test_curation_returns_matching_colors_and_items(client, db_session):
    _seed_curation_data(db_session)
    profile_id = _create_profile(client)
    client.post(f"/profiles/{profile_id}/analysis")

    response = client.get(f"/profiles/{profile_id}/curation")
    assert response.status_code == 200
    body = response.json()

    assert body["missing_elements"] == ["금"]
    assert {c["element"] for c in body["colors"]} == {"금"}
    assert {c["color_name"] for c in body["colors"]} == {"흰색", "은색"}
    assert {i["element"] for i in body["items"]} == {"금"}
    assert {i["name"] for i in body["items"]} == {"화이트 셔츠"}
