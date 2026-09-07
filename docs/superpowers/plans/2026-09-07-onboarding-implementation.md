# 온보딩 기능 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 사주 온보딩(생년월일/출생시간/성별/태어난 지역) 입력·조회·수정을 백엔드(FastAPI+PostgreSQL)와 프론트(Next.js)로 끝까지 연동해 동작시킨다.

**Architecture:** FastAPI 라우터 하나(`/profiles`)가 SQLAlchemy `Profile` 모델을 CRUD(생성/조회/부분수정)하고, Pydantic 스키마 하나(`ProfileBase`)의 검증 로직을 생성·수정 양쪽에서 재사용한다. 인증 시스템이 아직 없으므로 발급된 UUID 자체가 조회/수정 키 역할을 한다(스펙 4.3). 프론트는 폼 컴포넌트 하나를 생성/수정 화면에서 재사용한다.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 (Mapped/mapped_column), Alembic, Pydantic v2, pytest + httpx(TestClient), Next.js App Router + TypeScript + Tailwind.

**Spec:** `docs/superpowers/specs/2026-09-07-phase1-architecture-design.md` (4장 "오늘 구현 범위: 온보딩")

## Global Constraints

- DB 로컬 접속: `postgresql+psycopg://ohangfit:ohangfit@localhost:5433/ohangfit` (docker-compose db 호스트 포트 5433 — `backend/app/config.py` 기본값과 동일). 테스트/마이그레이션 실행 전 `docker compose up -d db` 필요
- 검증 규칙은 스펙 4.2 그대로: `birth_date`는 1900-01-01 이상 오늘 이하, `birth_time_unknown=false`면 `birth_time` 필수·`true`면 `birth_time`은 저장 안 함, `gender`는 `male`/`female`, `birth_region`은 공백 불가
- API는 스펙 4.3 그대로: `POST /profiles`, `GET /profiles/{id}`, `PATCH /profiles/{id}` (없는 id는 404)
- **커밋/푸시는 사용자가 직접 실행한다 (`GIT_WORKFLOW.md`).** 이 플랜의 어떤 단계에서도 `git commit`/`git push`를 실행하지 말 것 — 각 태스크 마지막에 사용자에게 실행할 정확한 명령어를 안내하는 것으로 대체
- 프론트엔드 자동화 테스트 프레임워크는 아직 없음. `ponytail:` 폼 하나짜리 화면에 vitest/RTL을 새로 들이는 건 과함 — 반복되는 화면이 늘어나면 그때 도입. 대신 Task 8에서 실제 두 서버를 띄운 수동/curl 연동 검증으로 대체
- 백엔드는 `backend/` 디렉토리에서 실행/테스트한다 (`cd backend && ...`). `app` 패키지 임포트는 `backend/conftest.py`가 pytest에 `backend/`를 sys.path로 잡아주는 것에 의존

---

### Task 1: SQLAlchemy `Profile` 모델

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/profile.py`
- Test: `backend/tests/test_profile_model.py`
- Test: `backend/conftest.py` (pytest가 `backend/`를 sys.path에 넣도록 하는 빈 루트 conftest — 아직 fixture 없음)
- Modify: `backend/requirements.txt`

**Interfaces:**
- Produces: `app.models.profile.Profile` (SQLAlchemy 모델, `__tablename__ = "profiles"`, 컬럼: `id, birth_date, birth_time, birth_time_unknown, gender, birth_region, created_at, updated_at`) — Task 2(마이그레이션), Task 4(라우터)가 사용

- [ ] **Step 1: requirements.txt에 pytest 추가**

`backend/requirements.txt`에 아래 줄 추가:

```
pytest==9.1.1
```

- [ ] **Step 2: 설치**

Run: `cd backend && .venv/bin/pip install -r requirements.txt`
Expected: `pytest` 설치 성공

- [ ] **Step 3: 빈 루트 conftest.py 생성 (sys.path용)**

`backend/conftest.py`:

```python
# pytest가 이 파일을 기준으로 backend/ 를 sys.path에 추가해줘서 `import app`이 동작함.
# DB fixture는 Task 4에서 추가.
```

- [ ] **Step 4: 실패하는 테스트 작성**

`backend/tests/test_profile_model.py`:

```python
from app.models.profile import Profile


def test_profile_table_name():
    assert Profile.__tablename__ == "profiles"


def test_profile_columns():
    columns = {c.name for c in Profile.__table__.columns}
    assert columns == {
        "id",
        "birth_date",
        "birth_time",
        "birth_time_unknown",
        "gender",
        "birth_region",
        "created_at",
        "updated_at",
    }
```

- [ ] **Step 5: 테스트 실행해서 실패 확인**

Run: `cd backend && .venv/bin/pytest tests/test_profile_model.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.models'`

- [ ] **Step 6: `app/models/__init__.py` 생성 (빈 파일)**

`backend/app/models/__init__.py`:

```python
```

- [ ] **Step 7: `Profile` 모델 구현**

`backend/app/models/profile.py`:

```python
import uuid
from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, String, Time, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    birth_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    birth_time_unknown: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    birth_region: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

- [ ] **Step 8: 테스트 실행해서 통과 확인**

Run: `cd backend && .venv/bin/pytest tests/test_profile_model.py -v`
Expected: PASS (2 passed)

- [ ] **Step 9: 커밋 명령어 안내 (직접 커밋하지 말 것)**

사용자에게 아래 명령어를 안내:

```bash
git add backend/app/models backend/tests/test_profile_model.py backend/conftest.py backend/requirements.txt
git commit -m "feat: Profile SQLAlchemy 모델 추가"
```

---

### Task 2: Alembic 마이그레이션

**Files:**
- Modify: `backend/alembic/env.py`
- Create: `backend/alembic/versions/<autogenerated>.py`

**Interfaces:**
- Consumes: `app.models.profile.Profile` (Task 1), `app.db.Base` (기존)
- Produces: DB에 실제 `profiles` 테이블 (Task 4 통합 테스트가 이 테이블에 의존)

- [ ] **Step 1: env.py에 모델 import 등록**

`backend/alembic/env.py`에서 아래 줄을 찾아:

```python
# from app.models import onboarding  # noqa: F401  (모델 생기면 여기 추가)
```

다음으로 교체:

```python
from app.models import profile  # noqa: F401
```

- [ ] **Step 2: DB 컨테이너 기동 확인**

Run: `cd /Users/hanminjeong/orca/projects/OhangFit && docker compose up -d db`
Expected: `ohangfit-db-1` Running

- [ ] **Step 3: 마이그레이션 자동 생성**

Run: `cd backend && .venv/bin/alembic revision --autogenerate -m "create profiles table"`
Expected: `backend/alembic/versions/`에 새 파일 생성, 로그에 `Detected added table 'profiles'` 포함

- [ ] **Step 4: 생성된 마이그레이션 파일 검증**

생성된 파일을 열어 `upgrade()` 함수가 `op.create_table("profiles", ...)`를 포함하고, 아래 8개 컬럼이 모두 있는지 확인 (없으면 Step 1의 import가 적용 안 된 것이므로 재확인):
`id`(UUID, primary_key), `birth_date`(Date, nullable=False), `birth_time`(Time, nullable=True), `birth_time_unknown`(Boolean, nullable=False), `gender`(String, nullable=False), `birth_region`(String, nullable=False), `created_at`(DateTime, nullable=False), `updated_at`(DateTime, nullable=False)

- [ ] **Step 5: 마이그레이션 적용**

Run: `cd backend && .venv/bin/alembic upgrade head`
Expected: `Running upgrade -> <revision>, create profiles table`

- [ ] **Step 6: 테이블 존재 확인**

Run: `cd backend && .venv/bin/alembic current`
Expected: 방금 만든 revision이 head로 표시됨 (에러 없이)

- [ ] **Step 7: 커밋 명령어 안내**

```bash
git add backend/alembic
git commit -m "feat: profiles 테이블 마이그레이션 추가"
```

---

### Task 3: Pydantic 스키마 (검증 로직)

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/profile.py`
- Test: `backend/tests/test_profile_schema.py`

**Interfaces:**
- Produces: `app.schemas.profile.Gender`(str Enum: `male`, `female`), `ProfileBase`, `ProfileCreate`, `ProfileUpdate`(모든 필드 Optional), `ProfileRead`(id/created_at/updated_at 포함, `model_config = {"from_attributes": True}`) — Task 4(라우터)가 사용

- [ ] **Step 1: 실패하는 테스트 작성**

`backend/tests/test_profile_schema.py`:

```python
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
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `cd backend && .venv/bin/pytest tests/test_profile_schema.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.schemas'`

- [ ] **Step 3: `app/schemas/__init__.py` 생성 (빈 파일)**

`backend/app/schemas/__init__.py`:

```python
```

- [ ] **Step 4: 스키마 구현**

`backend/app/schemas/profile.py`:

```python
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
```

- [ ] **Step 5: 테스트 실행해서 통과 확인**

Run: `cd backend && .venv/bin/pytest tests/test_profile_schema.py -v`
Expected: PASS (6 passed)

- [ ] **Step 6: 커밋 명령어 안내**

```bash
git add backend/app/schemas backend/tests/test_profile_schema.py
git commit -m "feat: 온보딩 Pydantic 스키마 및 검증 로직 추가"
```

---

### Task 4: FastAPI 라우터 (`/profiles`) + 통합 테스트

**Files:**
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/profiles.py`
- Modify: `backend/conftest.py` (DB 세션/클라이언트 fixture 추가)
- Modify: `backend/app/main.py` (라우터 등록 — 실행 중 발견: 이 태스크의 통합 테스트가 `app`에 라우터가 마운트돼 있어야 동작하므로, 원래 Task 5 Step1이던 등록을 여기로 옮김)
- Test: `backend/tests/test_profiles_api.py`
- Modify: `backend/requirements.txt`

**Interfaces:**
- Consumes: `app.models.profile.Profile`(Task 1), `app.schemas.profile.*`(Task 3), `app.db.get_db`(기존)
- Produces: `app.routers.profiles.router` (APIRouter, prefix `/profiles`) — Task 5가 `app.main`에 등록

- [ ] **Step 1: requirements.txt에 httpx 추가 (TestClient용)**

`backend/requirements.txt`에 추가:

```
httpx==0.28.1
```

Run: `cd backend && .venv/bin/pip install -r requirements.txt`

- [ ] **Step 2: conftest.py에 DB fixture 추가**

`backend/conftest.py` 전체를 아래로 교체:

```python
# pytest가 이 파일을 기준으로 backend/ 를 sys.path에 추가해줘서 `import app`이 동작함.
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.db import Base, engine, get_db
from app.main import app
from app.models import profile  # noqa: F401  Base.metadata에 테이블 등록


@pytest.fixture(scope="session", autouse=True)
def _tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    testing_session = sessionmaker(bind=connection)()
    yield testing_session
    testing_session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

- [ ] **Step 3: 실패하는 테스트 작성**

`backend/tests/test_profiles_api.py`:

```python
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
```

- [ ] **Step 4: 테스트 실행해서 실패 확인**

Run: `cd backend && .venv/bin/pytest tests/test_profiles_api.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.routers'`

- [ ] **Step 5: `app/routers/__init__.py` 생성 (빈 파일)**

`backend/app/routers/__init__.py`:

```python
```

- [ ] **Step 6: 라우터 구현**

`backend/app/routers/profiles.py`:

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.profile import Profile
from app.schemas.profile import ProfileBase, ProfileCreate, ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _assign_fields(profile: Profile, validated: ProfileBase) -> None:
    profile.birth_date = validated.birth_date
    profile.birth_time = validated.birth_time
    profile.birth_time_unknown = validated.birth_time_unknown
    profile.gender = validated.gender.value
    profile.birth_region = validated.birth_region


@router.post("", response_model=ProfileRead, status_code=201)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)) -> Profile:
    profile = Profile()
    _assign_fields(profile, payload)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=ProfileRead)
def get_profile(profile_id: UUID, db: Session = Depends(get_db)) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")
    return profile


@router.patch("/{profile_id}", response_model=ProfileRead)
def update_profile(
    profile_id: UUID, payload: ProfileUpdate, db: Session = Depends(get_db)
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")

    current = {
        "birth_date": profile.birth_date,
        "birth_time": profile.birth_time,
        "birth_time_unknown": profile.birth_time_unknown,
        "gender": profile.gender,
        "birth_region": profile.birth_region,
    }
    current.update(payload.model_dump(exclude_unset=True))

    try:
        validated = ProfileCreate(**current)
    except ValidationError as exc:
        # ponytail: exc.errors()의 "input"에 date/time 같은 non-JSON 값이 그대로 들어있어서
        # jsonable_encoder로 감싸지 않으면 여기서 500이 남 (FastAPI가 HTTPException.detail을
        # 자동으로 인코딩해주지 않음)
        raise HTTPException(
            status_code=422, detail=jsonable_encoder(exc.errors())
        ) from exc

    _assign_fields(profile, validated)
    db.commit()
    db.refresh(profile)
    return profile
```

- [ ] **Step 6a: main.py에 라우터 등록** (원래 Task 5 Step1이었으나, 이 태스크의 통합 테스트가 통과하려면 여기서 먼저 등록해야 해서 이동함)

`backend/app/main.py`에서:

```python
from app.config import settings
from app.db import get_db
```

다음으로 교체:

```python
from app.config import settings
from app.db import get_db
from app.routers.profiles import router as profiles_router
```

그리고 파일 마지막에 추가:

```python
app.include_router(profiles_router)
```

- [ ] **Step 7: 테스트 실행해서 통과 확인**

Run: `cd backend && .venv/bin/pytest tests/test_profiles_api.py -v`
Expected: PASS (7 passed) — `docker compose up -d db`가 떠 있어야 함(Global Constraints 참고)

- [ ] **Step 8: 전체 백엔드 테스트 스위트 통과 확인**

Run: `cd backend && .venv/bin/pytest -v`
Expected: 이 태스크까지의 모든 테스트(모델/스키마/API) PASS

- [ ] **Step 9: 커밋 명령어 안내**

```bash
git add backend/app/routers backend/app/main.py backend/conftest.py backend/tests/test_profiles_api.py backend/requirements.txt
git commit -m "feat: /profiles CRUD API 구현 및 라우터 등록"
```

---

### Task 5: 컨테이너 스모크 테스트

**Files:**
- (수정 없음 — Task 4에서 라우터 등록까지 이미 끝남. 이 태스크는 도커 환경에서 실제로 동작하는지 확인만 한다)

**Interfaces:**
- Consumes: `app.routers.profiles.router`, 이미 `app.main`에 등록됨 (Task 4)

- [ ] **Step 1: 도커로 재빌드/기동**

Run: `cd /Users/hanminjeong/orca/projects/OhangFit && docker compose up -d --build`
Expected: `backend`, `db` 컨테이너 모두 Running

- [ ] **Step 2: 컨테이너 안에서 실제 API 스모크 테스트**

Run:
```bash
curl -s -X POST http://localhost:8000/profiles \
  -H "Content-Type: application/json" \
  -d '{"birth_date":"1990-05-20","birth_time":"10:30:00","birth_time_unknown":false,"gender":"female","birth_region":"서울"}'
```
Expected: HTTP 201, 응답 JSON에 `id` 필드 포함. 이어서 그 `id`로 `curl http://localhost:8000/profiles/<id>` 실행 시 동일 데이터 반환 확인

- [ ] **Step 3: 컨테이너 정리**

Run: `docker compose down`

(커밋 없음 — 이 태스크는 코드 변경이 없는 검증 전용 태스크)

---

### Task 6: 프론트엔드 — 온보딩 입력 폼

**Files:**
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/components/OnboardingForm.tsx`
- Create: `frontend/src/app/onboarding/page.tsx`

**Interfaces:**
- Produces: `createProfile`, `getProfile`, `updateProfile` (frontend/src/lib/api.ts) — Task 7이 `getProfile`/`updateProfile` 사용
- Produces: `<OnboardingForm initialValues? submitLabel onSubmit>` 컴포넌트 — Task 7이 재사용

- [ ] **Step 1: API 클라이언트 작성**

`frontend/src/lib/api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Gender = "male" | "female";

export interface ProfileInput {
  birth_date: string; // YYYY-MM-DD
  birth_time: string | null; // HH:MM:SS
  birth_time_unknown: boolean;
  gender: Gender;
  birth_region: string;
}

export interface Profile extends ProfileInput {
  id: string;
  created_at: string;
  updated_at: string;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: null }));
    const detail = (body as { detail?: unknown }).detail;
    throw new Error(
      typeof detail === "string" ? detail : "요청을 처리하지 못했습니다."
    );
  }
  return response.json() as Promise<T>;
}

export async function createProfile(input: ProfileInput): Promise<Profile> {
  const response = await fetch(`${API_BASE_URL}/profiles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return handleResponse<Profile>(response);
}

export async function getProfile(id: string): Promise<Profile> {
  const response = await fetch(`${API_BASE_URL}/profiles/${id}`);
  return handleResponse<Profile>(response);
}

export async function updateProfile(
  id: string,
  input: Partial<ProfileInput>
): Promise<Profile> {
  const response = await fetch(`${API_BASE_URL}/profiles/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return handleResponse<Profile>(response);
}
```

- [ ] **Step 2: 재사용 폼 컴포넌트 작성**

`frontend/src/components/OnboardingForm.tsx`:

```tsx
"use client";

import { useState, FormEvent } from "react";
import type { Gender, ProfileInput } from "@/lib/api";

export interface OnboardingFormProps {
  initialValues?: ProfileInput;
  submitLabel: string;
  onSubmit: (values: ProfileInput) => Promise<void>;
}

export function OnboardingForm({
  initialValues,
  submitLabel,
  onSubmit,
}: OnboardingFormProps) {
  const [birthDate, setBirthDate] = useState(initialValues?.birth_date ?? "");
  const [birthTime, setBirthTime] = useState(initialValues?.birth_time ?? "");
  const [birthTimeUnknown, setBirthTimeUnknown] = useState(
    initialValues?.birth_time_unknown ?? false
  );
  const [gender, setGender] = useState<Gender>(initialValues?.gender ?? "female");
  const [birthRegion, setBirthRegion] = useState(initialValues?.birth_region ?? "");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit({
        birth_date: birthDate,
        birth_time: birthTimeUnknown ? null : birthTime,
        birth_time_unknown: birthTimeUnknown,
        gender,
        birth_region: birthRegion,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-sm">
      <label className="flex flex-col gap-1">
        생년월일
        <input
          type="date"
          required
          value={birthDate}
          onChange={(e) => setBirthDate(e.target.value)}
          className="border rounded px-3 py-2"
        />
      </label>

      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={birthTimeUnknown}
          onChange={(e) => setBirthTimeUnknown(e.target.checked)}
        />
        출생시간을 몰라요
      </label>

      {!birthTimeUnknown && (
        <label className="flex flex-col gap-1">
          출생시간
          <input
            type="time"
            required={!birthTimeUnknown}
            step={1}
            value={birthTime ?? ""}
            onChange={(e) => setBirthTime(e.target.value)}
            className="border rounded px-3 py-2"
          />
        </label>
      )}

      <label className="flex flex-col gap-1">
        성별
        <select
          value={gender}
          onChange={(e) => setGender(e.target.value as Gender)}
          className="border rounded px-3 py-2"
        >
          <option value="female">여성</option>
          <option value="male">남성</option>
        </select>
      </label>

      <label className="flex flex-col gap-1">
        태어난 지역
        <input
          type="text"
          required
          placeholder="예: 서울특별시"
          value={birthRegion}
          onChange={(e) => setBirthRegion(e.target.value)}
          className="border rounded px-3 py-2"
        />
      </label>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="bg-black text-white rounded px-4 py-2 disabled:opacity-50"
      >
        {submitting ? "처리 중..." : submitLabel}
      </button>
    </form>
  );
}
```

- [ ] **Step 3: 온보딩 페이지 작성**

`frontend/src/app/onboarding/page.tsx`:

```tsx
"use client";

import { useRouter } from "next/navigation";
import { OnboardingForm } from "@/components/OnboardingForm";
import { createProfile } from "@/lib/api";
import type { ProfileInput } from "@/lib/api";

export default function OnboardingPage() {
  const router = useRouter();

  async function handleSubmit(values: ProfileInput) {
    const profile = await createProfile(values);
    router.push(`/onboarding/${profile.id}`);
  }

  return (
    <main className="p-6">
      <h1 className="text-xl font-bold mb-4">사주 정보 입력</h1>
      <OnboardingForm submitLabel="저장하기" onSubmit={handleSubmit} />
    </main>
  );
}
```

- [ ] **Step 4: 타입/빌드 체크**

Run: `cd frontend && npm run build`
Expected: 빌드 성공 (타입 에러 없음)

- [ ] **Step 5: 커밋 명령어 안내**

```bash
git add frontend/src/lib/api.ts frontend/src/components/OnboardingForm.tsx frontend/src/app/onboarding/page.tsx
git commit -m "feat: 온보딩 입력 폼 화면 구현"
```

---

### Task 7: 프론트엔드 — 조회/수정 화면

**Files:**
- Create: `frontend/src/app/onboarding/[id]/page.tsx`

**Interfaces:**
- Consumes: `getProfile`, `updateProfile`, `<OnboardingForm>` (Task 6)

- [ ] **Step 1: 조회/수정 페이지 작성**

`frontend/src/app/onboarding/[id]/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { OnboardingForm } from "@/components/OnboardingForm";
import { getProfile, updateProfile } from "@/lib/api";
import type { Profile, ProfileInput } from "@/lib/api";

export default function ProfileDetailPage() {
  const params = useParams<{ id: string }>();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProfile(params.id)
      .then(setProfile)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "불러오지 못했습니다.")
      );
  }, [params.id]);

  async function handleUpdate(values: ProfileInput) {
    const updated = await updateProfile(params.id, values);
    setProfile(updated);
    setEditing(false);
  }

  if (error) return <main className="p-6 text-red-600">{error}</main>;
  if (!profile) return <main className="p-6">불러오는 중...</main>;

  if (editing) {
    return (
      <main className="p-6">
        <h1 className="text-xl font-bold mb-4">정보 수정</h1>
        <OnboardingForm
          initialValues={profile}
          submitLabel="수정 완료"
          onSubmit={handleUpdate}
        />
      </main>
    );
  }

  return (
    <main className="p-6">
      <h1 className="text-xl font-bold mb-4">저장된 사주 정보</h1>
      <dl className="flex flex-col gap-2 mb-4">
        <div>생년월일: {profile.birth_date}</div>
        <div>출생시간: {profile.birth_time_unknown ? "모름" : profile.birth_time}</div>
        <div>성별: {profile.gender === "male" ? "남성" : "여성"}</div>
        <div>태어난 지역: {profile.birth_region}</div>
      </dl>
      <button onClick={() => setEditing(true)} className="border rounded px-4 py-2">
        수정하기
      </button>
    </main>
  );
}
```

- [ ] **Step 2: 타입/빌드 체크**

Run: `cd frontend && npm run build`
Expected: 빌드 성공

- [ ] **Step 3: 커밋 명령어 안내**

```bash
git add frontend/src/app/onboarding/[id]/page.tsx
git commit -m "feat: 온보딩 결과 조회/수정 화면 구현"
```

---

### Task 8: 전체 연동 검증 + 문서 갱신

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: 전체 백엔드(Task 1-5) + 프론트(Task 6-7)

- [ ] **Step 1: 백엔드+DB 기동**

Run: `cd /Users/hanminjeong/orca/projects/OhangFit && docker compose up -d --build`
Expected: `backend`, `db` Running

- [ ] **Step 2: 프론트 개발 서버 기동**

Run: `cd frontend && npm run dev &`
Expected: `http://localhost:3000`에서 서빙 시작 로그

- [ ] **Step 3: 온보딩 페이지 로드 확인**

Run: `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/onboarding`
Expected: `200`

- [ ] **Step 4: 브라우저(또는 브라우저 자동화 도구)로 실제 폼 제출까지 확인**

`http://localhost:3000/onboarding`에서 폼을 채워 제출 → `/onboarding/{id}`로 리다이렉트되어 저장된 값이 보이는지 확인 → "수정하기" 클릭 → 지역 값 변경 후 제출 → 변경된 값이 화면에 반영되는지 확인. (브라우저 자동화 도구가 없는 실행 환경이면 이 단계는 사용자에게 직접 확인을 요청)

- [ ] **Step 5: 정리**

Run: `docker compose down` 및 프론트 dev 서버 종료(`kill %1` 또는 해당 백그라운드 프로세스 종료)

- [ ] **Step 6: CLAUDE.md 갱신**

`CLAUDE.md`의 "디렉토리 구조" 섹션에 아래 항목 추가 (backend `/app` 트리 하위):

```
    /models   → SQLAlchemy 모델 (Profile 등)
    /schemas  → Pydantic 스키마
    /routers  → API 라우터
  /tests      → pytest
```

그리고 frontend 트리에:

```
  /src
    /app/onboarding       → 온보딩 입력/조회/수정 화면
    /components           → 재사용 컴포넌트 (OnboardingForm 등)
    /lib/api.ts            → 백엔드 API 클라이언트
```

"진행 상황" 섹션의 Phase 1 항목을 아래로 갱신:

```
- [ ] Phase 1 (MVP) — 진행 중 (온보딩 완료, 분석/큐레이션/결제/공유 남음)
```

- [ ] **Step 7: 커밋 명령어 안내**

```bash
git add CLAUDE.md
git commit -m "docs: 온보딩 기능 완료 반영"
```
