from sqlalchemy.exc import IntegrityError

from domain.card_repository import (
    DuplicateCardException,
    MissingCardException,
)
from services.unit_of_work import AbstractUnitOfWork
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
            if not relevance:
                relevance = Relevance(description=relevance_description)
                uow.relevance_levels.add(relevance)
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


def update_existing_card(
    id_card: int,
    new_word_type: WordType,
    new_relevance_description: str,
    new_german: str,
    new_italian: str,
    uow: AbstractUnitOfWork,
) -> None:
    with uow:
        card = uow.cards.get(id=id_card)
        if not card:
            raise MissingCardException()
        card.word_type = new_word_type
        card.german = new_german
        card.italian = new_italian

        relevance = uow.relevance_levels.get_by_description(new_relevance_description)
        if not relevance:
            relevance = Relevance(description=new_relevance_description)
            uow.relevance_levels.add(relevance)
        
        card.relevance = relevance
        uow.commit()
