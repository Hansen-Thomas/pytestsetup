import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

import database
import database.orm as orm


@pytest.fixture
def engine():
    engine = create_engine(database.URL_OBJECT_UNIT_TESTS, echo=True)
    database.metadata.drop_all(bind=engine)
    database.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session(engine):
    orm.start_mappers()
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    clear_mappers()
