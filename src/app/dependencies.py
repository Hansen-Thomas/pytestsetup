import database


def get_session_factory():
    return database.get_session_factory()
