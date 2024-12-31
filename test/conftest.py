import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, clear_mappers

import database
import database.orm as orm
import database.unit_of_work as unit_of_work


@pytest.fixture()
def reset_db_for_e2e_tests():
    # get engine for local unit-test-db:
    url_key = "local_db_unit_tests"
    engine = database._get_engine(url_key=url_key, echo=True)

    # reset schema:
    database.metadata.drop_all(bind=engine)
    database.metadata.create_all(bind=engine)

    # overwrite DEFAULT_SESSION_FACTORY in database.unit_of_work 
    # to ignore the USE-DB-variable from config-file but anyway
    # use the local-db-for-unit-tests. This way we can use all
    # normal elements of our app including the database-setup but
    # just point it to the database of our choice:
    e2e_session_maker = sessionmaker(bind=engine)
    unit_of_work.DEFAULT_SESSION_FACTORY = e2e_session_maker

    # continue with normal app flow:
    orm.start_mappers()
    yield
    clear_mappers()


@pytest.fixture
def unit_test_engine() -> Engine:
    url_key = "local_db_unit_tests"
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
