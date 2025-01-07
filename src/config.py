import os


def get_postgres_uri():
    host = os.environ.get('DB_HOST', 'localhost')
    port = 54321 if host == 'localhost' else 5432
    db_name_stage = os.environ.get('DB_NAME_STAGE', 'unknown_stage_db')
    user = os.environ.get('DB_USER', 'unknow_user')
    password = os.environ.get('DB_PASSWORD', 'abc123')
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name_stage}"


def get_api_url():
    host = os.environ.get('API_HOST', 'localhost')
    port = 5005 if host == 'localhost' else 80
    return f"http://{host}:{port}"
