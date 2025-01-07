from sqlalchemy.exc import IntegrityError

from domain.card_repository import (
    DuplicateCardException,
    MissingCardException,
)
from domain.card import Card
from domain.relevance import Relevance
from domain.word_type import WordType
from services.unit_of_work import AbstractUnitOfWork


def create_card_in_db(
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
    

def read_card_in_db(id_card, uow: AbstractUnitOfWork) -> Card:
    pass


def update_card_in_db(
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


def delete_card_in_db(id_card: int, uow: AbstractUnitOfWork) -> None:
    with uow:
        card_to_delete = uow.cards.get(id=id_card)
        if not card_to_delete:
            raise MissingCardException()
        uow.cards.delete(card=card_to_delete)
        uow.commit()
