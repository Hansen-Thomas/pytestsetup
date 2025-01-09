from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import sessionmaker

import app.schemas.card as card_models
from app.dependencies import get_session_factory
from domain.card_repository import DuplicateCardException, MissingCardException
from services.card_services import (
    create_card_in_db,
    delete_card_in_db,
    read_all_cards_in_db,
    read_card_in_db,
    update_card_in_db,
)
from services.unit_of_work import DbUnitOfWork


router = APIRouter()


@router.post("/cards")
def add_card(
    card_input: card_models.PydCardInputModel,
    session_factory: sessionmaker = Depends(get_session_factory),
):
    try:
        create_card_in_db(
            word_type=card_input.word_type,
            relevance_description=card_input.relevance_description,
            german=card_input.german,
            italian=card_input.italian,
            uow=DbUnitOfWork(session_factory=session_factory),
        )
    except DuplicateCardException:
        raise HTTPException(status_code=400, detail="Card already exists!")
    # TODO: Response genauer definieren


@router.get("/cards")
def get_all_cards(session_factory: sessionmaker = Depends(get_session_factory)):
    uow = DbUnitOfWork(
        session_factory=session_factory,
        session_shall_expire_on_commit=False,
    )
    domain_cards = read_all_cards_in_db(uow=uow)
    try:
        cards = [card_models.convert_to_pydantic(card) for card in domain_cards]
    except Exception as e:
        print(f"{e=}")
    return {"result": cards}


@router.get("/cards/{id_card}")
def get_card(
    id_card: int,
    session_factory: sessionmaker = Depends(get_session_factory),
):
    try:
        read_card_in_db(
            id_card=id_card,
            uow=DbUnitOfWork(session_factory=session_factory),
        )
    except MissingCardException:
        raise HTTPException(status_code=404, detail="Card does not exist!")
    # TODO: Response genauer definieren


@router.put("/cards/{id_card}")
def update_card(
    id_card: int,
    card_input: card_models.PydCardInputModel,
    session_factory: sessionmaker = Depends(get_session_factory),
):
    try:
        update_card_in_db(
            id_card=id_card,
            new_word_type=card_input.word_type,
            new_relevance_description=card_input.relevance_description,
            new_german=card_input.german,
            new_italian=card_input.italian,
            uow=DbUnitOfWork(session_factory=session_factory),
        )
    except MissingCardException:
        raise HTTPException(status_code=404, detail="Card does not exist!")
    # TODO: Response genauer definieren


@router.delete("/cards/{id_card}")
def delete_card(
    id_card: int,
    session_factory: sessionmaker = Depends(get_session_factory),
):
    try:
        delete_card_in_db(
            id_card=id_card,
            uow=DbUnitOfWork(session_factory=session_factory),
        )
    except MissingCardException:
        raise HTTPException(status_code=404, detail="Card does not exist!")
