from sqlalchemy import Engine, text


def test_connection_can_persist_data_in_unit_test_db(unit_test_engine: Engine):
    """
    Ensures that SqlAlchemy can reach the database and persist data.
    """
    # Arrange:
    with unit_test_engine.connect() as connection:
        # insert relevance-records to use the later as foreign-keys:
        stmt_insert_relevance = text(
            """
            INSERT INTO Relevance (id, name) VALUES (:id, :name)
            """
        )
        records_relevance = [
            {"id": 1, "name": "A - Beginner"},
            {"id": 2, "name": "B - Intermediate"},
            {"id": 3, "name": "C - Professional"},
        ]
        connection.execute(stmt_insert_relevance, parameters=records_relevance)

        # insert cards (referencing the relevance records):
        stmt_insert_cards = text(
            """
            INSERT INTO Card (word_type, id_relevance, german, italian)
            VALUES (:word_type, :id_relevance, :german, :italian)
            """
        )
        records_cards = [
            {
                "word_type": "NOUN",
                "id_relevance": 1,
                "german": "das Haus",
                "italian": "la casa",
            },
            {
                "word_type": "NOUN",
                "id_relevance": 2,
                "german": "der Baum",
                "italian": "l'albero",
            },
        ]
        connection.execute(stmt_insert_cards, parameters=records_cards)
        connection.commit()

    # Act & Assert:
    with unit_test_engine.connect() as connection_2:
        stmt_select_cards = text(
            """
            SELECT id, word_type, id_relevance, german, italian FROM Card
            """
        )
        result = connection_2.execute(stmt_select_cards).all()

        assert result
        expected = [
            (1, "NOUN", 1, "das Haus", "la casa"),
            (2, "NOUN", 2, "der Baum", "l'albero"),
        ]
        for row in result:
            assert row in expected


def test_connection_does_not_persist_without_commit(unit_test_engine: Engine):
    """
    Ensures that SqlAlchemy only persists if transations are commited.
    """
    # Arrange:
    with unit_test_engine.connect() as connection:
        # insert relevance-records to use the later as foreign-keys:
        stmt_insert_relevance = text(
            """
            INSERT INTO Relevance (id, name) VALUES (:id, :name)
            """
        )
        records_relevance = [
            {"id": 1, "name": "A - Beginner"},
            {"id": 2, "name": "B - Intermediate"},
            {"id": 3, "name": "C - Professional"},
        ]
        connection.execute(stmt_insert_relevance, parameters=records_relevance)

        stmt_insert_cards = text(
            """
            INSERT INTO Card (word_type, id_relevance, german, italian)
            VALUES (:word_type, :id_relevance, :german, :italian)
            """
        )
        records_cards = [
            {
                "word_type": "NOUN",
                "id_relevance": 1,
                "german": "das Haus",
                "italian": "la casa",
            },
            {
                "word_type": "NOUN",
                "id_relevance": 2,
                "german": "der Baum",
                "italian": "l'albero",
            },
        ]
        connection.execute(stmt_insert_cards, parameters=records_cards)
        # no commit! -> no effect in database

    # Act & Assert:
    with unit_test_engine.connect() as connection_2:
        stmt_select_cards = text(
            """
            SELECT id, word_type, id_relevance, german, italian FROM Card
            """
        )
        result = connection_2.execute(stmt_select_cards).all()

        assert not result  # since not commited
