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


def _create_lead(client, email="signup@example.com"):
    profile_id = _create_profile(client)
    client.post("/leads", json={"profile_id": profile_id, "email": email})
    return profile_id


def test_signup_converts_existing_lead(client):
    profile_id = _create_lead(client, email="lead@example.com")
    response = client.post(
        "/signup", json={"email": "lead@example.com", "password": "pw123456"}
    )
    assert response.status_code == 200
    assert response.json()["profile_id"] == profile_id


def test_signup_without_prior_lead_returns_404_profile(client):
    response = client.post(
        "/signup", json={"email": "fresh@example.com", "password": "pw123456"}
    )
    assert response.status_code == 404


def test_signup_rejects_already_member_email(client):
    _create_lead(client, email="dup@example.com")
    client.post("/signup", json={"email": "dup@example.com", "password": "pw123456"})

    response = client.post(
        "/signup", json={"email": "dup@example.com", "password": "another"}
    )
    assert response.status_code == 409


def test_login_success(client):
    profile_id = _create_lead(client, email="login@example.com")
    client.post("/signup", json={"email": "login@example.com", "password": "pw123456"})

    response = client.post(
        "/login", json={"email": "login@example.com", "password": "pw123456"}
    )
    assert response.status_code == 200
    assert response.json()["profile_id"] == profile_id


def test_login_wrong_password(client):
    _create_lead(client, email="wrongpw@example.com")
    client.post(
        "/signup", json={"email": "wrongpw@example.com", "password": "correct-pw"}
    )

    response = client.post(
        "/login", json={"email": "wrongpw@example.com", "password": "incorrect"}
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/login", json={"email": "nobody@example.com", "password": "whatever"}
    )
    assert response.status_code == 401
