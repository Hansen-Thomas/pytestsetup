from sqlalchemy.exc import IntegrityError

from database.repositories.card_repository import DuplicateCardException
from database.unit_of_work import AbstractUnitOfWork
from domain.card import Card
from domain.relevance import Relevance
from domain.word_type import WordType


def add_new_card(
    word_type: WordType,
    relevance_description: str,
    german: str,
    italian: str,
    uow: AbstractUnitOfWork,
) -> None:
    try:
        with uow:
            relevance = uow.relevance_levels.get_by_description(
                description=relevance_description
            )
            new_card = Card(
                word_type=word_type,
                relevance=relevance,
                german=german,
                italian=italian,
            )
            uow.cards.add(new_card)
            uow.commit()
    except IntegrityError:
        raise DuplicateCardException()
