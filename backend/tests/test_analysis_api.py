def _create_profile(client, **overrides):
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


def test_create_analysis(client):
    profile_id = _create_profile(client)
    response = client.post(f"/profiles/{profile_id}/analysis")
    assert response.status_code == 200
    body = response.json()
    assert body["profile_id"] == profile_id
    assert set(body["five_elements"].keys()) == {"목", "화", "토", "금", "수"}
    assert sum(body["five_elements"].values()) == 8
    assert body["missing_elements"]
    assert body["excess_elements"]
    assert body["sinsal"] == []


def test_create_analysis_profile_not_found(client):
    response = client.post("/profiles/00000000-0000-0000-0000-000000000000/analysis")
    assert response.status_code == 404


def test_get_analysis_before_created_returns_404(client):
    profile_id = _create_profile(client)
    response = client.get(f"/profiles/{profile_id}/analysis")
    assert response.status_code == 404


def test_get_analysis_after_created(client):
    profile_id = _create_profile(client)
    client.post(f"/profiles/{profile_id}/analysis")
    response = client.get(f"/profiles/{profile_id}/analysis")
    assert response.status_code == 200
    assert response.json()["profile_id"] == profile_id


def test_analysis_same_profile_data_gives_same_result(client):
    profile_id = _create_profile(client)
    first = client.post(f"/profiles/{profile_id}/analysis").json()
    second = client.post(f"/profiles/{profile_id}/analysis").json()
    assert first["five_elements"] == second["five_elements"]
    assert first["id"] == second["id"]  # upsert, 새 row가 아니라 같은 row 갱신


def test_analysis_recomputes_after_profile_edit(client):
    profile_id = _create_profile(client)
    first = client.post(f"/profiles/{profile_id}/analysis").json()
    client.patch(f"/profiles/{profile_id}", json={"birth_date": "1985-11-03"})
    second = client.post(f"/profiles/{profile_id}/analysis").json()
    assert first["five_elements"] != second["five_elements"]
    assert first["id"] == second["id"]
