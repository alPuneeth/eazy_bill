import uuid
import pytest

from fastapi import FastAPI
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient

from app.db.session import get_session
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_admin
from app.main import app as fastapi_app
from app.core.config import settings
from app.models.core_models.user import User, UserRole
from tests.factories.user import create_admin, create_user

fastapi_app:FastAPI

TEST_DATABASE_URL = settings.test_database_url

@pytest.fixture(scope="session")
def engine():
    assert "test" in TEST_DATABASE_URL.lower(), "Unsafe DB!"

    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
        )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    connection.begin_nested() # SAVEPOINT

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def admin_user(session):
    user = create_admin(session)
    session.commit()
    return user


@pytest.fixture(scope="function")
def client(session, admin_user):

    def override_get_session():
        yield session

    def override_require_admin():
        return True # bypass RBAC
    
    def override_get_current_user():
        return admin_user
    
    fastapi_app.dependency_overrides[get_session] = override_get_session
    fastapi_app.dependency_overrides[require_admin] = override_require_admin
    fastapi_app.dependency_overrides[get_current_user] = override_get_current_user


    with TestClient(fastapi_app) as c:
        yield c
    
    fastapi_app.dependency_overrides.pop(get_session, None)
    fastapi_app.dependency_overrides.pop(require_admin, None)
    fastapi_app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="function")
def raw_client(session):
    def override_get_session():
        yield session
    
    fastapi_app.dependency_overrides[get_session] = override_get_session

    with TestClient(fastapi_app) as c:
        yield c
    
    fastapi_app.dependency_overrides.pop(get_session, None)

