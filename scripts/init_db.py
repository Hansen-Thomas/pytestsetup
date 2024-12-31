import database


def setup_schema():
    stage_engine = database._get_engine(url_key="stage")
    database._setup_schema(engine=stage_engine)


if __name__ == "__main__":
    setup_schema()
