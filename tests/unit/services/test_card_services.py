import pytest

from app.schemas.card import PydCardInput
from domain.card_repository import DuplicateCardException, MissingCardException
from domain.card import Card
from domain.relevance import Relevance
from domain.word_type import WordType
from services.cards.crud import create_card_in_db, delete_card_in_db, update_card_in_db
from services.unit_of_work import FakeUnitOfWork, DbUnitOfWork


def test_new_card_can_be_added(session_factory):
    uow = DbUnitOfWork(session_factory=session_factory)
    create_card_in_db(
        word_type=WordType.NOUN,
        relevance_description="A - Beginner",
        german="das Haus",
        italian="la casa",
        uow=uow,
    )
    with uow:
        all_cards = uow.cards.all()
        assert len(all_cards) == 1
        new_card = all_cards[0]
        assert new_card.german == "das Haus"
        assert new_card.italian == "la casa"
        assert new_card.word_type == WordType.NOUN
        assert new_card.relevance == Relevance(description="A - Beginner")


def test_duplicate_card_can_not_be_added():
    uow = FakeUnitOfWork()
    create_card_in_db(
        word_type=WordType.NONE,
        relevance_description="A - Beginner",
        german="das Haus",
        italian="la casa",
        uow=uow,
    )
    with pytest.raises(DuplicateCardException):
        create_card_in_db(
            word_type=WordType.NONE,
            relevance_description="A - Beginner",
            german="das Haus",
            italian="la casa",
            uow=uow,
        )
    with uow:
        all_cards = uow.cards.all()
        assert len(all_cards) == 1


def test_update_existing_card():
    uow = FakeUnitOfWork()
    existing_card = Card(
        id=4711,
        word_type=WordType.VERB,
        id_relevance=1,
        relevance=Relevance(
            id=1,
            description="A - Beginner",
        ),
        german="der Baum",
        italian="l'albero",
    )
    uow.cards.add(existing_card)

    updated_card_input = PydCardInput(
        word_type=WordType.NOUN,
        relevance_description="A - Beginner",
        german="der Baum",
        italian="l'albero",
    )

    update_card_in_db(
        id_card=4711,
        new_word_type=updated_card_input.word_type,
        new_relevance_description=updated_card_input.relevance_description,
        new_german=updated_card_input.german,
        new_italian=updated_card_input.italian,
        uow=uow,
    )

    with uow:
        card = uow.cards.get(id=4711)
        assert card
        assert card.word_type == WordType.NOUN
        assert card.relevance.description == "A - Beginner"
        assert card.german == "der Baum"
        assert card.italian == "l'albero"


def test_missing_card_can_not_be_updated():
    uow = FakeUnitOfWork()
    # uow.cards stays empty

    updated_card_input = PydCardInput(
        word_type=WordType.NOUN,
        relevance_description="A - Beginner",
        german="der Baum",
        italian="l'albero",
    )

    with pytest.raises(MissingCardException):
        update_card_in_db(
            id_card=4711,  # does not exist
            new_word_type=updated_card_input.word_type,
            new_relevance_description=updated_card_input.relevance_description,
            new_german=updated_card_input.german,
            new_italian=updated_card_input.italian,
            uow=uow,
        )
    with uow:
        all_cards = uow.cards.all()
        assert not all_cards


def test_delete_card():
    uow = FakeUnitOfWork()
    card_to_delete = Card(
        id=4711,
        word_type=WordType.ADJECTIVE,
        relevance=Relevance(id=3, description="C - Professional"),
        german="weit",
        italian="large",
    )
    second_card = Card(
        id=4712,
        word_type=WordType.NOUN,
        relevance=Relevance(id=1, description="A - Beginner"),
        german="das Boot",
        italian="la barca",
    )
    with uow:
        uow.cards.add(card_to_delete)
        uow.cards.add(second_card)
        uow.commit()

    delete_card_in_db(id_card=4711, uow=uow)

    # inspect result:
    with uow:
        cards = uow.cards.all()
        assert len(cards) == 1
        result_card = cards[0]
        assert result_card.id == 4712


def test_missing_card_can_not_be_deleted():
    uow = FakeUnitOfWork()
    card = Card(
        id=4711,
        word_type=WordType.ADJECTIVE,
        relevance=Relevance(id=3, description="C - Professional"),
        german="weit",
        italian="large",
    )

    with uow:
        uow.cards.add(card)
        uow.commit()

    with pytest.raises(MissingCardException):
        delete_card_in_db(id_card=4712, uow=uow)  # wrong id, does not exist!

    # inspect result:
    with uow:
        cards = uow.cards.all()
        assert len(cards) == 1
        result_card = cards[0]
        assert result_card.id == 4711
