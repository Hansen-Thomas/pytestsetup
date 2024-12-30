from fastapi import APIRouter
from pydantic import BaseModel

from database.unit_of_work import DbUnitOfWork
from domain.word_type import WordType
from services.card_services import add_new_card


router = APIRouter()


class CardInputModel(BaseModel):
    word_type: WordType
    relevance_description: str
    german: str
    italian: str


@router.post("/cards")
def add_card(card: CardInputModel):
    uow = DbUnitOfWork()
    add_new_card(
        word_type=card.word_type,
        relevance_description=card.relevance_description,
        german=card.german,
        italian=card.italian,
        uow=uow,
    )
