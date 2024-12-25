import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

import database
import database.orm as orm
from test.utils.fake_session import FakeSession


@pytest.fixture
def fake_session():
    return FakeSession()


@pytest.fixture
def engine():
    engine = create_engine("sqlite:///pytest.db")
    database.metadata.drop_all(bind=engine)
    database.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session(engine):
    orm.start_mappers()
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    clear_mappers()
