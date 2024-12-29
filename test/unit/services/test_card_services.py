import pytest

from database.repositories.card_repository import DuplicateCardException
from database.unit_of_work import FakeUnitOfWork, DbUnitOfWork
from domain.relevance import Relevance
from domain.word_type import WordType
from services.card_services import add_new_card


def test_new_card_can_be_added():
    uow = FakeUnitOfWork()
    word_type = WordType.NONE
    relevance = Relevance(name="A")
    add_new_card(
        word_type=word_type,
        relevance=relevance,
        german="das Haus",
        italian="la casa",
        uow=uow,
    )
    with uow:
        all_cards = uow.cards.all()
        assert all_cards


def test_duplicate_card_can_not_be_added(session_factory):
    # uow = FakeUnitOfWork()
    uow = DbUnitOfWork(session_factory=session_factory)
    word_type = WordType.NONE
    relevance = Relevance(name="A")
    add_new_card(
        word_type=word_type,
        relevance=relevance,
        german="das Haus",
        italian="la casa",
        uow=uow,
    )
    with pytest.raises(DuplicateCardException):
        add_new_card(
            word_type=word_type,
            relevance=relevance,
            german="das Haus",
            italian="la casa",
            uow=uow,
        )
