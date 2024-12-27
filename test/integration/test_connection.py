from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

import test.integration.integration_utils as plain_sql_utils


def test_session_can_save_and_load_data(local_unit_test_db_engine: Engine):
    # Arrange:
    session_factory = sessionmaker(bind=local_unit_test_db_engine)
    session_to_insert = session_factory()
    records = [
        {"id": 1, "german": "das Haus", "italian": "la casa"},
        {"id": 2, "german": "der Baum", "italian": "l'albero"},
    ]
    plain_sql_utils.insert_cards(session=session_to_insert, records=records)
    session_to_insert.commit()
    session_to_insert.close()

    # Act:
    session_to_select: Session = session_factory()
    result = plain_sql_utils.select_all_cards(session=session_to_select)
    session_to_select.close()

    # Assert:
    expected = [
        (1, "das Haus", "la casa"),
        (2, "der Baum", "l'albero"),
    ]
    for row in result:
        assert row in expected
