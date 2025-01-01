from fastapi.testclient import TestClient
import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from app.main import app
from app.dependencies import get_session_factory
import database
import database.orm as orm


@pytest.fixture(name="client")  
def client_fixture(session_factory: sessionmaker):  
    def get_session_factory_override():  
        return session_factory

    app.dependency_overrides[get_session_factory] = get_session_factory_override  

    client = TestClient(app)  
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def unit_test_engine() -> Engine:
    url_key = "local_db_unit_tests"
    # url_key = "in_memory_db_unit_tests"
    engine = database._get_engine(url_key=url_key, echo=True)
    database.metadata.drop_all(bind=engine)
    database.metadata.create_all(bind=engine)
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
