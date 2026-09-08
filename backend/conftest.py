# pytest가 이 파일을 기준으로 backend/ 를 sys.path에 추가해줘서 `import app`이 동작함.
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.db import Base, engine, get_db
from app.main import app
from app.models import account, profile  # noqa: F401  Base.metadata에 테이블 등록


@pytest.fixture(scope="session", autouse=True)
def _tables():
    # ponytail: drop_all teardown removed — this runs against the shared dev DB
    # (same one Alembic manages), and dropping it desyncs Alembic's bookkeeping
    # from actual schema state. create_all is idempotent and just a safety net
    # for a fresh DB with no migrations applied yet. Per-test isolation is fully
    # handled by db_session's transaction rollback below.
    Base.metadata.create_all(engine)


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
