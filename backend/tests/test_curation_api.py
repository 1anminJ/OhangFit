import uuid

from app.models.color_mapping import ColorMapping
from app.models.curation_item import CurationItem
from app.models.payment import Payment
from app.models.profile import Profile


def _create_profile(client, **overrides):
    # 1990-05-20 / 10:30:00 은 MockSajuAdapter로 항상 missing_elements=["금"]을 낸다.
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
                element="금",
                name="화이트 셔츠",
                category="아우터",
                image_url="https://example.com/1.jpg",
            ),
            CurationItem(
                element="화",
                name="빨강 스카프",
                category="액세서리",
                image_url="https://example.com/2.jpg",
            ),
        ]
    )
    db_session.commit()


def test_curation_requires_email_first(client):
    profile_id = _create_profile(client)
    client.post(f"/profiles/{profile_id}/analysis")

    response = client.get(f"/profiles/{profile_id}/curation")
    assert response.status_code == 403


def test_curation_profile_not_found(client):
    response = client.get(f"/profiles/{uuid.uuid4()}/curation")
    assert response.status_code == 404


def test_curation_requires_analysis(client):
    profile_id = _create_profile(client)
    client.post(
        "/leads", json={"profile_id": profile_id, "email": "noanalysis@example.com"}
    )

    response = client.get(f"/profiles/{profile_id}/curation")
    assert response.status_code == 404


def test_curation_locked_before_payment(client, db_session):
    _seed_curation_data(db_session)
    profile_id = _create_profile(client)
    client.post(f"/profiles/{profile_id}/analysis")
    client.post(
        "/leads", json={"profile_id": profile_id, "email": "unpaid@example.com"}
    )

    response = client.get(f"/profiles/{profile_id}/curation")
    assert response.status_code == 200
    body = response.json()
    assert body["locked"] is True
    assert body["missing_elements"] == ["금"]
    assert body["colors"] == []
    assert body["items"] == []


def test_curation_unlocked_after_payment(client, db_session):
    _seed_curation_data(db_session)
    profile_id = _create_profile(client)
    client.post(f"/profiles/{profile_id}/analysis")
    client.post("/leads", json={"profile_id": profile_id, "email": "paid@example.com"})
    client.post("/signup", json={"email": "paid@example.com", "password": "pw123456"})
    client.post(f"/profiles/{profile_id}/payment")

    response = client.get(f"/profiles/{profile_id}/curation")
    assert response.status_code == 200
    body = response.json()
    assert body["locked"] is False
    assert {c["element"] for c in body["colors"]} == {"금"}
    assert {i["element"] for i in body["items"]} == {"금"}


def test_payment_does_not_unlock_other_profile_on_same_account(client, db_session):
    # profile A: 리드 → 회원가입 → 결제 완료
    _seed_curation_data(db_session)
    profile_a_id = _create_profile(client)
    client.post(f"/profiles/{profile_a_id}/analysis")
    client.post(
        "/leads", json={"profile_id": profile_a_id, "email": "hijack@example.com"}
    )
    client.post("/signup", json={"email": "hijack@example.com", "password": "pw123456"})
    client.post(f"/profiles/{profile_a_id}/payment")

    response_a = client.get(f"/profiles/{profile_a_id}/curation")
    assert response_a.status_code == 200
    assert response_a.json()["locked"] is False

    # profile B: 같은(이미 결제된) 이메일로 리드 등록 → 계정이 B로 재연결됨
    profile_b_id = _create_profile(client)
    client.post(f"/profiles/{profile_b_id}/analysis")
    client.post(
        "/leads", json={"profile_id": profile_b_id, "email": "hijack@example.com"}
    )

    # A는 계정 연결을 잃었으므로 이메일 게이트에 걸림
    response_a_after = client.get(f"/profiles/{profile_a_id}/curation")
    assert response_a_after.status_code == 403

    # B는 같은 계정을 갖게 됐지만, Payment는 A의 profile_id로 스코핑되어 있으므로 잠김 유지
    response_b = client.get(f"/profiles/{profile_b_id}/curation")
    assert response_b.status_code == 200
    assert response_b.json()["locked"] is True


def test_failed_payment_does_not_unlock_curation(client, db_session):
    _seed_curation_data(db_session)
    profile_id = _create_profile(client)
    client.post(f"/profiles/{profile_id}/analysis")
    client.post(
        "/leads", json={"profile_id": profile_id, "email": "failedpay@example.com"}
    )
    profile = db_session.get(Profile, uuid.UUID(profile_id))
    db_session.add(
        Payment(
            account_id=profile.account_id,
            profile_id=profile.id,
            amount=9900,
            status="failed",
            paid_at=None,
        )
    )
    db_session.commit()

    response = client.get(f"/profiles/{profile_id}/curation")
    assert response.status_code == 200
    assert response.json()["locked"] is True
