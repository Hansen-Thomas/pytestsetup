from sqlalchemy import Engine, text


def test_connection_can_persist_data_in_unit_test_db(unit_test_engine: Engine):
    # Arrange:
    with unit_test_engine.connect() as connection:
        stmt = text(
            """
            INSERT INTO Card (word_type, german, italian)
            VALUES (:word_type, :german, :italian)
            """
        )
        records = [
            {
                "word_type": "NOUN",
                "german": "das Haus",
                "italian": "la casa",
            },
            {
                "word_type": "NOUN",
                "german": "der Baum",
                "italian": "l'albero",
            },
        ]
        connection.execute(stmt, parameters=records)
        connection.commit()

    # Act & Assert:
    with unit_test_engine.connect() as connection_2:
        stmt = text(
        """
        SELECT id, word_type, german, italian FROM Card
        """
        )
        result = connection_2.execute(stmt).all()

        assert result
        expected = [
            (1, "NOUN", "das Haus", "la casa"),
            (2, "NOUN", "der Baum", "l'albero"),
        ]
        for row in result:
            assert row in expected


def test_connection_does_not_persist_without_commit(unit_test_engine: Engine):
    # Arrange:
    with unit_test_engine.connect() as connection:
        stmt = text(
            """
            INSERT INTO Card (word_type, german, italian)
            VALUES (:word_type, :german, :italian)
            """
        )
        records = [
            {
                "word_type": "NOUN",
                "german": "das Haus",
                "italian": "la casa",
            },
            {
                "word_type": "NOUN",
                "german": "der Baum",
                "italian": "l'albero",
            },
        ]
        connection.execute(stmt, parameters=records)
        # no commit! -> no effect in database

    # Act & Assert:
    with unit_test_engine.connect() as connection_2:
        stmt = text(
        """
        SELECT id, word_type, german, italian FROM Card
        """
        )
        result = connection_2.execute(stmt).all()

        assert not result  # since not commited

