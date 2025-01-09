import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.unit_of_work import DbUnitOfWork
from domain.card import Card
from domain.tag import Tag
import tests.integration.integration_utils as plain_sql_utils


def test_uow_can_get_card_and_add_tags_to_it(session_factory):
    # Arrange:
    session: Session = session_factory()
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

    # Act:
    uow = DbUnitOfWork(session_factory)
    with uow:
        card = uow.cards.get(id=7)
        if card:
            card.add_tag("Sprache")
            card.add_tag("Test-Tag")
        tag = Tag(value="Tiere")
        uow.tags.add(tag)
        uow.commit()

    # Assert:
    stmt_card = select(Card).where(Card.id == 7)
    card = session.scalar(stmt_card)
    assert card
    expected_card_tag_values = ["Sprache", "Test-Tag"]
    for value in expected_card_tag_values:
        assert card.has_tag(value)

    stmt_tags = select(Tag)
    tags = session.scalars(stmt_tags).all()
    expected_tag_values = ["Sprache", "Test-Tag", "Tiere"]
    assert len(tags) == 3
    for tag in tags:
        assert tag.value in expected_tag_values


def test_uow_rolls_back_uncommitted_work_by_default(session_factory):
    # Arrange:
    session: Session = session_factory()
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

    # Act:
    uow = DbUnitOfWork(session_factory)
    with uow:
        card = uow.cards.get(id=7)
        if card:
            card.add_tag("Sprache")
            card.add_tag("Test-Tag")
        # no commit!

    # Assert:
    stmt = select(Card).where(Card.id == 7)
    card = session.scalar(stmt)
    assert card
    assert list(card.tags) == []


def test_uow_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = DbUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
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
            plain_sql_utils.insert_cards(session=uow.session, records=records)
            raise MyException()  # -> rollback!

    new_session: Session = session_factory()
    stmt = select(Card)
    cards = new_session.scalars(stmt).all()
    assert cards == []
