from sqlalchemy.orm import sessionmaker

import test.integration.integration_utils as plain_sql_utils


def test_sqlalchemy_can_persist_data_in_unit_test_db(unit_test_engine):
    # Arrange:
    session_factory = sessionmaker(bind=unit_test_engine)

    session_to_insert = session_factory()
    records = [
        {
            "id": 1,
            "word_type": "NOUN",
            "german": "das Haus",
            "italian": "la casa",
        },
        {
            "id": 2,
            "word_type": "NOUN",
            "german": "der Baum",
            "italian": "l'albero",
        },
    ]
    plain_sql_utils.insert_cards(session=session_to_insert, records=records)
    session_to_insert.commit()
    session_to_insert.close()

    # Act:
    session_to_select = session_factory()
    result = plain_sql_utils.select_all_cards(session=session_to_select)
    session_to_select.close()

    # Assert:
    assert result
    expected = [
        (1, "NOUN", "das Haus", "la casa"),
        (2, "NOUN", "der Baum", "l'albero"),
    ]
    for row in result:
        assert row in expected


def test_sqlalchemy_does_not_persist_without_commit(unit_test_engine):
    # Arrange:
    session_factory = sessionmaker(bind=unit_test_engine)

    session_to_insert = session_factory()
    records = [
        {
            "id": 1,
            "word_type": "NOUN",
            "german": "das Haus",
            "italian": "la casa",
        },
        {
            "id": 2,
            "word_type": "NOUN",
            "german": "der Baum",
            "italian": "l'albero",
        },
    ]
    plain_sql_utils.insert_cards(session=session_to_insert, records=records)
    # no commit! -> no effect in database
    session_to_insert.close()

    # Act:
    session_to_select = session_factory()
    result = plain_sql_utils.select_all_cards(session=session_to_select)
    session_to_select.close()

    # Assert:
    assert not result  # since not commited
