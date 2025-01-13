from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import sessionmaker

from app.dependencies import get_session_factory
import app.schemas.card as schemas
from core.exceptions import DuplicateResourceError, ResourceNotFoundError
import core.services.cards.crud as crud
import core.services.unit_of_work as uow


router = APIRouter()


@router.post(
    "/cards",
    response_model=schemas.PydCard,
    status_code=status.HTTP_201_CREATED,
)
def create_card(
    card_input: schemas.PydCardInput,
    session_factory: sessionmaker = Depends(get_session_factory),
) -> Any:
    try:
        new_card = crud.create_card_in_db(
            word_type=card_input.word_type,
            relevance_description=card_input.relevance_description,
            german=card_input.german,
            italian=card_input.italian,
            uow=uow.DbUnitOfWork(session_factory=session_factory),
        )
        return schemas.convert_to_pydantic(new_card)
    except DuplicateResourceError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card already exists.",
        )


@router.get("/cards", response_model=list[schemas.PydCard])
def read_cards(
    session_factory: sessionmaker = Depends(get_session_factory),
) -> Any:
    domain_cards = crud.read_cards_from_db(
        uow=uow.DbUnitOfWork(session_factory=session_factory)
    )
    pyd_cards = list(map(schemas.convert_to_pydantic, domain_cards))
    return pyd_cards


@router.get("/cards/{id_card}", response_model=schemas.PydCardResponse)
def read_card(
    id_card: int,
    session_factory: sessionmaker = Depends(get_session_factory),
) -> Any:
    try:
        domain_card = crud.read_card_from_db(
            id_card=id_card,
            uow=uow.DbUnitOfWork(session_factory=session_factory),
        )
        return schemas.convert_to_pydantic(domain_card)
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found.",
        )


@router.put("/cards/{id_card}", response_model=schemas.PydCardResponse)
def update_card(
    id_card: int,
    card_input: schemas.PydCardInput,
    session_factory: sessionmaker = Depends(get_session_factory),
) -> Any:
    try:
        domain_card = crud.update_card_in_db(
            id_card=id_card,
            **card_input.model_dump(),
            uow=uow.DbUnitOfWork(session_factory=session_factory),
        )
        return schemas.convert_to_pydantic(domain_card)
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found.",
        )


@router.delete("/cards/{id_card}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    id_card: int,
    session_factory: sessionmaker = Depends(get_session_factory),
):
    try:
        crud.delete_card_in_db(
            id_card=id_card,
            uow=uow.DbUnitOfWork(session_factory=session_factory),
        )
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found.",
        )
