from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.passwords import hash_password
from src.db.base import Base
from src.db.session import get_db
from src.main import app
from src.models import *  # noqa: F401,F403
from src.models.role import Role
from src.models.user import User

TEST_DB_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    roles = [Role(name="Viewer"), Role(name="Analyst"), Role(name="Approver"), Role(name="Admin")]
    db.add_all(roles)
    db.flush()

    role_map = {r.name: r.id for r in db.query(Role).all()}
    users = [
        User(username="admin", password=hash_password("admin123"), role_id=role_map["Admin"], status="ACTIVE"),
        User(username="analyst", password=hash_password("analyst123"), role_id=role_map["Analyst"], status="ACTIVE"),
        User(username="approver", password=hash_password("approver123"), role_id=role_map["Approver"], status="ACTIVE"),
        User(username="viewer", password=hash_password("viewer123"), role_id=role_map["Viewer"], status="ACTIVE"),
    ]
    db.add_all(users)
    db.commit()
    db.close()
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _login(client: TestClient, username: str, password: str) -> dict:
    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture
def admin_token(client: TestClient) -> str:
    return _login(client, "admin", "admin123")["access_token"]


@pytest.fixture
def analyst_token(client: TestClient) -> str:
    return _login(client, "analyst", "analyst123")["access_token"]


@pytest.fixture
def approver_token(client: TestClient) -> str:
    return _login(client, "approver", "approver123")["access_token"]


@pytest.fixture
def viewer_token(client: TestClient) -> str:
    return _login(client, "viewer", "viewer123")["access_token"]
