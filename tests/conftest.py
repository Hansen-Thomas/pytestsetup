from fastapi.testclient import TestClient
import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from app.main import app
from app.dependencies import get_session_factory
import db
import db.orm as orm


@pytest.fixture(name="client")
def client_fixture(session_factory: sessionmaker):
    # Overwrite the get_session_factory-dependency from our FastAPI-app
    # to ensure we alway use our unit_test_db with this Testclient. Thus,
    # since dependencies must be callables, create a local function that
    # just returns our test-session-factory-fixture:

    def get_session_factory_override():
        return session_factory

    app.dependency_overrides[get_session_factory] = get_session_factory_override
    # by that we ensured that we can use the normal app-code for testing
    # but for sure always use the session_factory from our test-suite (which
    # points to a testing database).

    # return the Testclient:
    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def unit_test_engine() -> Engine:
    url_key = "local_db_unit_tests"
    # url_key = "in_memory_db_unit_tests"

    # in_memory_db doesn't work with e2e-tests (FastAPI create multiple threads,
    # this seems to be part of the problem)

    engine = db._get_engine(url_key=url_key, echo=True)
    db.metadata.drop_all(bind=engine)
    db.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session_factory(unit_test_engine):
    orm.start_mappers()
    yield sessionmaker(bind=unit_test_engine)
    clear_mappers()


@pytest.fixture
def session(unit_test_engine):
    orm.start_mappers()
    with sessionmaker(bind=unit_test_engine)() as session:
        yield session
    clear_mappers()
