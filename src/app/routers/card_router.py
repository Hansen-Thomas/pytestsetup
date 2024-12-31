from fastapi import APIRouter

import app.api_models.card as card_models
from database.unit_of_work import DbUnitOfWork
from services.card_services import add_new_card


router = APIRouter()


@router.post("/cards")
def add_card(card_input: card_models.CardInputModel):
    add_new_card(
        word_type=card_input.word_type,
        relevance_description=card_input.relevance_description,
        german=card_input.german,
        italian=card_input.italian,
        uow=DbUnitOfWork(),
    )
