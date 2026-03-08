import os
import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.database import get_db
from app.models.base import Base
from main import app
from faker import Faker

fake = Faker("en_US")

TEST_DB_PATH = "./test.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        for tbl in reversed(Base.metadata.sorted_tables):
            session.execute(tbl.delete())
        session.commit()
        session.close()


@pytest.fixture(scope="function")
def fake_user_payload():
    return {
        "name": fake.name(),
        "email": "test@traderxai.com",
        "password": "123",
        "phone": fake.msisdn(),
        "active": True,
    }


@pytest.fixture(scope="function")
def fake_auth_payload():
    return {
        "email": "test@traderxai.com",
        "password": "123",
    }


@pytest.fixture(scope="function")
def fake_plan_payload():
    return {
        "name": "Premium Plan",
        "daily_amount": 10,
        "no_limit": False,
        "value": 9.99,
    }


@pytest.fixture
def fake_subscription_payload():
    def _factory(plan_id=None, user_id=None):
        return {
            "user_id": user_id,
            "plan_id": plan_id,
            "active": True,
            "canceled_at": None,
        }

    return _factory


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c
