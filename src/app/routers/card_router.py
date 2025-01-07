from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import sessionmaker

import app.api_models.card as card_models
from app.dependencies import get_session_factory
from database.repositories.card_repository import DuplicateCardException
from database.unit_of_work import DbUnitOfWork
from services.card_services import add_new_card, update_existing_card


router = APIRouter()


@router.post("/cards")
def add_card(
    card_input: card_models.CardInputModel,
    session_factory: sessionmaker = Depends(get_session_factory),
):
    try:
        add_new_card(
            word_type=card_input.word_type,
            relevance_description=card_input.relevance_description,
            german=card_input.german,
            italian=card_input.italian,
            uow=DbUnitOfWork(session_factory=session_factory),
        )
    except DuplicateCardException:
        raise HTTPException(status_code=400, detail="Card already exists!")


@router.patch("/cards/{id_card}")
def update_card(
    id_card: int,
    card_input: card_models.CardInputModel,
    session_factory: sessionmaker = Depends(get_session_factory),
):
    try:
        update_existing_card(
            id_card=id_card,
            new_word_type=card_input.word_type,
            new_relevance_description=card_input.relevance_description,
            new_german=card_input.german,
            new_italian=card_input.italian,
            uow=DbUnitOfWork(session_factory=session_factory),
        )
    except Exception as e:
        print(f"{e:}")
