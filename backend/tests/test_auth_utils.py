from app.auth_utils import hash_password, verify_password


def test_hash_and_verify_roundtrip():
    hashed = hash_password("my-secret-password")
    assert verify_password("my-secret-password", hashed) is True


def test_verify_rejects_wrong_password():
    hashed = hash_password("my-secret-password")
    assert verify_password("wrong-password", hashed) is False
