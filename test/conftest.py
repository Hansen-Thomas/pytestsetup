import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, clear_mappers

import database
import database.orm as orm


@pytest.fixture
def local_unit_test_db_engine() -> Engine:
    engine = database._get_engine("local_db_unit_tests", echo=True)
    database.metadata.drop_all(bind=engine)
    database.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session_factory(local_unit_test_db_engine):
    orm.start_mappers()
    yield sessionmaker(bind=local_unit_test_db_engine)
    clear_mappers()


@pytest.fixture
def session(local_unit_test_db_engine):
    orm.start_mappers()
    session = sessionmaker(bind=local_unit_test_db_engine)()
    yield session
    session.close()
    clear_mappers()
