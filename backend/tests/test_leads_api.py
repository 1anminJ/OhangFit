import uuid


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


def test_create_lead(client):
    profile_id = _create_profile(client)
    response = client.post(
        "/leads", json={"profile_id": profile_id, "email": "a@example.com"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "a@example.com"
    assert body["role"] == "lead"
    assert body["magic_link_url"].startswith("/magic-link/")


def test_create_lead_profile_not_found(client):
    response = client.post(
        "/leads", json={"profile_id": str(uuid.uuid4()), "email": "a@example.com"}
    )
    assert response.status_code == 404


def test_create_lead_reuses_existing_account(client):
    profile_id_1 = _create_profile(client)
    profile_id_2 = _create_profile(client)

    first = client.post(
        "/leads", json={"profile_id": profile_id_1, "email": "dup@example.com"}
    )
    second = client.post(
        "/leads", json={"profile_id": profile_id_2, "email": "dup@example.com"}
    )

    assert first.json()["account_id"] == second.json()["account_id"]

    token = second.json()["magic_link_url"].split("/")[-1]
    lookup = client.get(f"/leads/by-token/{token}")
    assert lookup.json()["profile_id"] == profile_id_2


def test_lead_by_token_returns_profile_id(client):
    profile_id = _create_profile(client)
    lead = client.post(
        "/leads", json={"profile_id": profile_id, "email": "b@example.com"}
    )
    token = lead.json()["magic_link_url"].split("/")[-1]

    response = client.get(f"/leads/by-token/{token}")
    assert response.status_code == 200
    assert response.json()["profile_id"] == profile_id


def test_lead_by_invalid_token(client):
    response = client.get("/leads/by-token/nonexistent-token")
    assert response.status_code == 404
