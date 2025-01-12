from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import sessionmaker

from app.dependencies import get_session_factory
import app.schemas.card as card_schemas
from domain.card_repository import DuplicateCardException
from services.cards.crud import (
    create_card_in_db,
    delete_card_in_db,
    read_all_cards_in_db,
    read_card_in_db,
    update_card_in_db,
)
from services.unit_of_work import DbUnitOfWork


router = APIRouter()


@router.post("/cards", status_code=status.HTTP_201_CREATED)
def add_card(
    card_input: card_schemas.PydCardInput,
    session_factory: sessionmaker = Depends(get_session_factory),
) -> card_schemas.PydCard:
    try:
        new_card = create_card_in_db(
            word_type=card_input.word_type,
            relevance_description=card_input.relevance_description,
            german=card_input.german,
            italian=card_input.italian,
            uow=DbUnitOfWork(session_factory=session_factory),
        )
        return card_schemas.convert_to_pydantic(new_card)
    except DuplicateCardException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card already exists.",
        )


@router.get("/cards")
def get_all_cards(
    session_factory: sessionmaker = Depends(get_session_factory),
) -> list[card_schemas.PydCard]:
    uow = DbUnitOfWork(session_factory=session_factory)
    domain_cards = read_all_cards_in_db(uow=uow)
    pyd_cards = list(map(card_schemas.convert_to_pydantic, domain_cards))
    return pyd_cards


@router.get("/cards/{id_card}")
def get_card(
    id_card: int,
    session_factory: sessionmaker = Depends(get_session_factory),
) -> card_schemas.PydCard:
    try:
        domain_card = read_card_in_db(
            id_card=id_card,
            uow=DbUnitOfWork(session_factory=session_factory),
        )
        return card_schemas.convert_to_pydantic(domain_card)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found.",
        )


@router.put("/cards/{id_card}")
def update_card(
    id_card: int,
    card_input: card_schemas.PydCardInput,
    session_factory: sessionmaker = Depends(get_session_factory),
) -> card_schemas.PydCard:
    try:
        domain_card = update_card_in_db(
            id_card=id_card,
            **card_input.model_dump(),
            uow=DbUnitOfWork(session_factory=session_factory),
        )
        return card_schemas.convert_to_pydantic(domain_card)
    except ValueError:
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
        delete_card_in_db(
            id_card=id_card,
            uow=DbUnitOfWork(session_factory=session_factory),
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found.",
        )

    # 400: Bad request      -> client-side input fails validation
    # 401: Unauthorized     -> user not authenticated
    # 403: Forbidden        -> user authenticated but not authorized
    # 404: Not found
    # 500: Internal server error -> should not be returned to user
