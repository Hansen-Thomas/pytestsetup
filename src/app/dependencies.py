from sqlalchemy.orm import sessionmaker

import core.db as db


def get_session_factory() -> sessionmaker:
    return db.get_session_factory()
