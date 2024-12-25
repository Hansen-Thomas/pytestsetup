from sqlalchemy import text
from sqlalchemy.orm import Session

from database.repositories.card_repository import DbCardRepository
from domain.card import Card

import test.integration.integration_utils as plain_sql_utils

def test_db_card_repo_can_add_card_with_tags(session: Session):
    # Arrange:
    card = Card()
    card.german = "die Natur"
    card.italian = "la natura"
    card.add_tag("Freizeit")
    card.add_tag("Person")

    # Act:
    card_repo = DbCardRepository(session)
    card_repo.add(card)
    session.commit()

    # Assert:

    # table Card:
    stmt_cards = text("SELECT id, german, italian FROM Card")
    result_cards = list(session.execute(stmt_cards))
    expected_cards = [(1, "die Natur", "la natura")]
    assert result_cards == expected_cards

    # table Tag:
    stmt_tags = text("SELECT id, value FROM Tag")
    result_tags = list(session.execute(stmt_tags))
    expected_values = ["Freizeit", "Person"]
    for result_tag in result_tags:
        (id, value) = result_tag
        assert value in expected_values

    # table Card_has_Tag:
    stmt_card_has_tag = text("SELECT id_card, id_tag FROM Card_has_Tag")
    result_card_has_tag = list(session.execute(stmt_card_has_tag))
    expected_id_couples = [(1, 1), (1, 2)]
    for id_couple in result_card_has_tag:
        assert id_couple in expected_id_couples


def test_db_card_repo_can_retrieve_card_with_tags(session: Session):
    # Arrange:
    records = [
        {"id": 7, "german": "die Frage", "italian": "la domanda"},
        {"id": 12, "german": "die Antwort", "italian": "la risposta"},
    ]
    plain_sql_utils.insert_cards(session=session, records=records)

    records = [{"id": 3, "value": "Sprache"}, {"id": 5, "value": "Essen"}]
    plain_sql_utils.insert_tags(session=session, records=records)
    
    records = [{"id_card": 7, "id_tag": 3}]
    plain_sql_utils.insert_associations(session=session, records=records)

    # Act:
    card_repo = DbCardRepository(session)
    card = card_repo.get(id=7)

    # Assert:
    assert card is not None
    assert card.german == "die Frage"
    assert card.italian == "la domanda"
    assert len(card.tags) == 1
    assert card.has_tag("Sprache")
