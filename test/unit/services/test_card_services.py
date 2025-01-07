import pytest

from app.api_models.card import PydCardInputModel
from domain.card_repository import DuplicateCardException, MissingCardException
from services.unit_of_work import FakeUnitOfWork, DbUnitOfWork
from domain.card import Card
from domain.relevance import Relevance
from domain.word_type import WordType
from services.card_services import add_new_card, update_existing_card


def test_new_card_can_be_added(session_factory):
    uow = DbUnitOfWork(session_factory=session_factory)
    add_new_card(
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
    add_new_card(
        word_type=WordType.NONE,
        relevance_description="A - Beginner",
        german="das Haus",
        italian="la casa",
        uow=uow,
    )
    with pytest.raises(DuplicateCardException):
        add_new_card(
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

    updated_card_input = PydCardInputModel(
        word_type=WordType.NOUN,
        relevance_description="A - Beginner",
        german="der Baum",
        italian="l'albero",
    )

    update_existing_card(
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

    updated_card_input = PydCardInputModel(
        word_type=WordType.NOUN,
        relevance_description="A - Beginner",
        german="der Baum",
        italian="l'albero",
    )

    with pytest.raises(MissingCardException):
        update_existing_card(
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
