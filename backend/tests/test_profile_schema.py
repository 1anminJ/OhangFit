from datetime import date, time

import pytest
from pydantic import ValidationError

from app.schemas.profile import Gender, ProfileCreate


def _valid_payload(**overrides):
    payload = {
        "birth_date": date(1990, 5, 20),
        "birth_time": time(10, 30),
        "birth_time_unknown": False,
        "gender": Gender.female,
        "birth_region": "서울",
    }
    payload.update(overrides)
    return payload


def test_valid_profile():
    profile = ProfileCreate(**_valid_payload())
    assert profile.birth_date == date(1990, 5, 20)
    assert profile.birth_time == time(10, 30)


def test_rejects_future_date():
    future = date(date.today().year + 1, 1, 1)
    with pytest.raises(ValidationError):
        ProfileCreate(**_valid_payload(birth_date=future))


def test_rejects_before_1900():
    with pytest.raises(ValidationError):
        ProfileCreate(**_valid_payload(birth_date=date(1899, 12, 31)))


def test_birth_time_unknown_clears_time():
    profile = ProfileCreate(
        **_valid_payload(birth_time_unknown=True, birth_time=time(10, 30))
    )
    assert profile.birth_time is None


def test_requires_birth_time_when_not_unknown():
    with pytest.raises(ValidationError):
        ProfileCreate(**_valid_payload(birth_time=None, birth_time_unknown=False))


def test_rejects_blank_region():
    with pytest.raises(ValidationError):
        ProfileCreate(**_valid_payload(birth_region="   "))
