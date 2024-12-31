import pytest

from database.repositories.card_repository import DuplicateCardException
from database.unit_of_work import FakeUnitOfWork, DbUnitOfWork
from domain.relevance import Relevance
from domain.word_type import WordType
from services.card_services import add_new_card


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


def test_duplicate_card_can_not_be_added(session_factory):
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
