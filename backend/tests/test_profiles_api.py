from datetime import date


def _valid_body(**overrides):
    body = {
        "birth_date": "1990-05-20",
        "birth_time": "10:30:00",
        "birth_time_unknown": False,
        "gender": "female",
        "birth_region": "서울",
    }
    body.update(overrides)
    return body


def test_create_profile(client):
    response = client.post("/profiles", json=_valid_body())
    assert response.status_code == 201
    body = response.json()
    assert body["birth_region"] == "서울"
    assert "id" in body


def test_create_profile_rejects_future_date(client):
    future = f"{date.today().year + 1}-01-01"
    response = client.post("/profiles", json=_valid_body(birth_date=future))
    assert response.status_code == 422


def test_get_profile(client):
    create_res = client.post("/profiles", json=_valid_body(birth_region="부산"))
    profile_id = create_res.json()["id"]

    response = client.get(f"/profiles/{profile_id}")
    assert response.status_code == 200
    assert response.json()["birth_region"] == "부산"


def test_get_profile_404(client):
    response = client.get("/profiles/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_profile(client):
    create_res = client.post("/profiles", json=_valid_body())
    profile_id = create_res.json()["id"]

    response = client.patch(f"/profiles/{profile_id}", json={"birth_region": "대구"})
    assert response.status_code == 200
    assert response.json()["birth_region"] == "대구"


def test_update_profile_invalid_merge_rejected(client):
    create_res = client.post("/profiles", json=_valid_body())
    profile_id = create_res.json()["id"]

    future = f"{date.today().year + 1}-01-01"
    response = client.patch(f"/profiles/{profile_id}", json={"birth_date": future})
    assert response.status_code == 422


def test_update_profile_404(client):
    response = client.patch(
        "/profiles/00000000-0000-0000-0000-000000000000",
        json={"birth_region": "대구"},
    )
    assert response.status_code == 404
