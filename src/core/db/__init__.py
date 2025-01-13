import logging
import os
from typing import Generator

from sqlalchemy import Connection, Engine, MetaData, URL, create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session

"""
This module provides basic database-access for all other modules of the
application via SqlAlchemy.

First the metadata-object of our SqlAlchemy-setup is initialized to define all
used tables. Then depending on the configuration-file connection-URLs are
constructed and stored in module-level variables.

Finally we provide functions to get a SqlAlchemy-Session and a SqlAlchemy-
Connection as our basic entry-points for DB-access with SqlAlchemy.

-------------------------------------------------------------------------------

Basic usage:
- import the module (e.g. as db)
- request a session or connection with a context-manager:
    - for a session: "with db.get_session() as session:"
    - for a connection: "with db.get_connection() as conn:"
- use the session or connection to query the database
- the session or connection will be closed automatically after the block

-------------------------------------------------------------------------------

Below you find two examples using a not existing Users-object and table with:


Example usage for a connection (so no ORM): -----------------------------------

    from sqlalchemy import text

    import infra.database as db

    stmt = text("SELECT * FROM users WHERE id = :id")

    with db.get_connection() as conn:
        result = conn.execute(stmt, {"id": 1}).fetchone()
        print(result)


Example usage for a session (with ORM): ---------------------------------------

    from sqlalchemy import select

    import infra.database as db
    import infra.database.orm as orm

    from domain.users import User

    orm.start_mappers()

    with db.get_session() as session:
        stmt = select(User).where(User.id == 1)
        user = session.execute(stmt).fetchone()
        print(user)

"""

# central SqlAlchemy setup: ===================================================


# 1) setup the database metadata: ---------------------------------------------


metadata = MetaData()
import core.db.tables  # ensures that all tables are loaded into the metadata.


# 2) setup the database-URL-objects: ------------------------------------------

_db_host = os.environ.get("DB_HOST", "localhost")
_db_port = os.environ.get("DB_PORT", 5432)
_db_name_stage = os.environ.get("DB_NAME_STAGE", "")
_db_user = os.environ.get("DB_USER", "")
_db_password = os.environ.get("DB_PASSWORD", "")

URL_OBJECT_PROD = URL.create(drivername="sqlite", database="production.db")
URL_OBJECT_STAGE = URL.create(
    drivername="postgresql+psycopg",
    host=_db_host,
    port=int(_db_port),
    database=_db_name_stage,
    username=_db_user,
    password=_db_password,
)
URL_OBJECT_UNIT_TESTS_LOCAL_DB = URL.create(drivername="sqlite", database="tests/pytest.db")
URL_OBJECT_UNIT_TESTS_IN_MEMORY = URL.create(drivername="sqlite", database=":memory:")

CONNECTION_URLS = {
    "production": URL_OBJECT_PROD,
    "stage": URL_OBJECT_STAGE,
    "local_db_unit_tests": URL_OBJECT_UNIT_TESTS_LOCAL_DB,
    "in_memory_db_unit_tests": URL_OBJECT_UNIT_TESTS_IN_MEMORY,
}

# 3) setup engine and sessionmaker: -------------------------------------------

_use_db = os.environ.get("USE_DB", "local_db_unit_tests")

if _use_db not in CONNECTION_URLS:
    raise ValueError(f'Value "{_use_db}" is not allowed for param "USE_DB"!')

logger = logging.getLogger(__name__)
logger.info(f"using database: {_use_db}")

_url_object = CONNECTION_URLS[_use_db]

if _use_db == "in_memory_db_unit_tests":
    _engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,
    )
else:
    _engine = create_engine(_url_object, echo=False)
_SessionFactory = sessionmaker(bind=_engine)


# 4) provide functions to get a connection and a session: ---------------------


def get_connection() -> Connection:
    return _engine.connect()


def get_session() -> Generator[Session, None, None]:
    with _SessionFactory() as session:
        yield session
        print(f"Status connection-pool: {_engine.pool.status()}")


def get_session_factory() -> sessionmaker:
    return _SessionFactory


# 5) Provide other utility functions: -----------------------------------------
#
#    These functions should not be used by the application, but only by
#    scripts or tests. They offer a way to retrieve an engine and to setup
#    the schema.


def _get_engine(url_key: str, echo: bool = False) -> Engine:
    if url_key not in CONNECTION_URLS:
        raise ValueError(f"url_key {url_key} not supported!")

    if _use_db == "in_memory_db_unit_tests":
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=True,
        )
    else:
        url_object = CONNECTION_URLS[url_key]
        engine = create_engine(url_object, echo=echo)
    return engine


def _setup_schema(engine: Engine) -> None:
    metadata.create_all(engine)
