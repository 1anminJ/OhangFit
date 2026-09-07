from datetime import date, datetime, time
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, model_validator

MIN_BIRTH_DATE = date(1900, 1, 1)


class Gender(str, Enum):
    male = "male"
    female = "female"


class ProfileBase(BaseModel):
    birth_date: date
    birth_time: time | None = None
    birth_time_unknown: bool = False
    gender: Gender
    birth_region: str

    @model_validator(mode="after")
    def validate_business_rules(self) -> "ProfileBase":
        if self.birth_date < MIN_BIRTH_DATE:
            raise ValueError("생년월일은 1900-01-01 이후여야 합니다.")
        if self.birth_date > date.today():
            raise ValueError("생년월일은 미래일 수 없습니다.")
        if not self.birth_region.strip():
            raise ValueError("태어난 지역을 입력해주세요.")
        if self.birth_time_unknown:
            self.birth_time = None
        elif self.birth_time is None:
            raise ValueError("출생시간을 모르면 '출생시간 모름'을 선택해주세요.")
        return self


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    birth_date: date | None = None
    birth_time: time | None = None
    birth_time_unknown: bool | None = None
    gender: Gender | None = None
    birth_region: str | None = None


class ProfileRead(ProfileBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
