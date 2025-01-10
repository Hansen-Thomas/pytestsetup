import db


def get_session_factory():
    return db.get_session_factory()
