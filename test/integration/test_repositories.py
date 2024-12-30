from sqlalchemy.orm import Session

from database.repositories.card_repository import DbCardRepository
from domain.card import Card
from domain.relevance import Relevance
from domain.word_type import WordType
import test.integration.integration_utils as plain_sql_utils


def test_db_card_repo_can_load_card_with_tags(session: Session):
    # Arrange:
    records = [
        {
            "id": 7,
            "word_type": "NOUN",
            "id_relevance": 1,
            "german": "die Frage",
            "italian": "la domanda",
        },
        {
            "id": 12,
            "word_type": "NOUN",
            "id_relevance": 1,
            "german": "die Antwort",
            "italian": "la risposta",
        },
    ]
    plain_sql_utils.insert_cards(session=session, records=records)
    session.commit()

    records = [{"id": 3, "value": "Sprache"}, {"id": 5, "value": "Essen"}]
    plain_sql_utils.insert_tags(session=session, records=records)
    session.commit()

    records = [{"id_card": 7, "id_tag": 3}]
    plain_sql_utils.insert_associations(session=session, records=records)
    session.commit()

    # Act:
    card_repo = DbCardRepository(session)
    card = card_repo.get(id=7)

    # Assert:
    assert card is not None
    assert card.word_type == WordType.NOUN
    assert card.id_relevance == 1
    assert card.german == "die Frage"
    assert card.italian == "la domanda"
    assert len(card.tags) == 1
    assert card.has_tag("Sprache")


def test_db_card_repo_can_save_card_with_tags(session: Session):
    # Arrange:
    card = Card(
        word_type=WordType.NOUN,
        relevance=Relevance(description="A - Beginner"),
        german="die Natur",
        italian="la natura",
    )
    card.add_tag("Freizeit")
    card.add_tag("Person")

    # Act:
    card_repo = DbCardRepository(session)
    card_repo.add(card)
    session.commit()

    # Assert:

    # table Card:
    result_cards = plain_sql_utils.select_all_cards(session=session)
    expected_cards = [(1, "NOUN", 1, "die Natur", "la natura")]
    assert result_cards == expected_cards

    # table Tag:
    result_tags = plain_sql_utils.select_all_tags(session=session)
    expected_values = ["Freizeit", "Person"]
    for result_tag in result_tags:
        (id, value) = result_tag
        assert value in expected_values

    # table Card_has_Tag:
    result_associations = plain_sql_utils.select_all_card_has_tag_associations(
        session=session
    )
    expected_id_couples = [(1, 1), (1, 2)]
    for id_couple in result_associations:
        assert id_couple in expected_id_couples
