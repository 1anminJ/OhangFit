import uuid

from sqlalchemy import select

from app.models.payment import Payment


def _create_profile(client):
    body = {
        "birth_date": "1990-05-20",
        "birth_time": "10:30:00",
        "birth_time_unknown": False,
        "gender": "female",
        "birth_region": "서울",
    }
    res = client.post("/profiles", json=body)
    return res.json()["id"]


def test_payment_requires_email_first(client):
    profile_id = _create_profile(client)
    response = client.post(f"/profiles/{profile_id}/payment")
    assert response.status_code == 404


def test_payment_requires_membership(client):
    profile_id = _create_profile(client)
    client.post(
        "/leads", json={"profile_id": profile_id, "email": "notmember@example.com"}
    )

    response = client.post(f"/profiles/{profile_id}/payment")
    assert response.status_code == 403


def test_payment_succeeds_for_member(client):
    profile_id = _create_profile(client)
    client.post("/leads", json={"profile_id": profile_id, "email": "payer@example.com"})
    client.post("/signup", json={"email": "payer@example.com", "password": "pw123456"})

    response = client.post(f"/profiles/{profile_id}/payment")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["amount"] == 9900


def test_payment_profile_not_found(client):
    response = client.post(f"/profiles/{uuid.uuid4()}/payment")
    assert response.status_code == 404


def test_payment_failure_returns_402_and_records_failed_payment(
    client, db_session, monkeypatch
):
    monkeypatch.setattr(
        "app.routers.payments._payment_adapter.charge", lambda amount: False
    )
    profile_id = _create_profile(client)
    client.post(
        "/leads", json={"profile_id": profile_id, "email": "declined@example.com"}
    )
    client.post(
        "/signup", json={"email": "declined@example.com", "password": "pw123456"}
    )

    response = client.post(f"/profiles/{profile_id}/payment")
    assert response.status_code == 402

    payment = db_session.execute(
        select(Payment).where(Payment.profile_id == uuid.UUID(profile_id))
    ).scalar_one()
    assert payment.status == "failed"
    assert payment.paid_at is None
