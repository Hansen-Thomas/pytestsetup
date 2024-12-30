import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, clear_mappers

import database
import database.orm as orm


@pytest.fixture()
def reset_db(url_key: str = "local_db_unit_tests"):
    engine = database._get_engine(url_key=url_key, echo=True)
    database.metadata.drop_all(bind=engine)
    database.metadata.create_all(bind=engine)
    orm.start_mappers()
    yield
    clear_mappers()


@pytest.fixture
def unit_test_engine(url_key: str = "local_db_unit_tests") -> Engine:
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
    session = sessionmaker(bind=unit_test_engine)()
    yield session
    session.close()
    clear_mappers()
