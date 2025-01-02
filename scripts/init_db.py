from sqlalchemy import text
import database


def setup_schema():
    stage_engine = database._get_engine(url_key="stage")
    # database._setup_schema(engine=stage_engine)


def can_connect_to_db():
    try:
        engine = database._get_engine(url_key="stage")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(e)
        return False


if __name__ == "__main__":
    # setup_schema()
    print(can_connect_to_db())
