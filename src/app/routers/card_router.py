from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import sessionmaker

from app.dependencies import get_session_factory
import app.schemas.card as schemas
from core.domain.card_repository import DuplicateCardException
import core.services.cards.crud as crud
import core.services.unit_of_work as uow


router = APIRouter()


@router.post("/cards", status_code=status.HTTP_201_CREATED)
def add_card(
    card_input: schemas.PydCardInput,
    session_factory: sessionmaker = Depends(get_session_factory),
) -> schemas.PydCard:
    try:
        new_card = crud.create_card_in_db(
            word_type=card_input.word_type,
            relevance_description=card_input.relevance_description,
            german=card_input.german,
            italian=card_input.italian,
            uow=uow.DbUnitOfWork(session_factory=session_factory),
        )
        return schemas.convert_to_pydantic(new_card)
    except DuplicateCardException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card already exists.",
        )


@router.get("/cards")
def get_all_cards(
    session_factory: sessionmaker = Depends(get_session_factory),
) -> list[schemas.PydCard]:
    domain_cards = crud.read_all_cards_in_db(
        uow=uow.DbUnitOfWork(session_factory=session_factory)
    )
    pyd_cards = list(map(schemas.convert_to_pydantic, domain_cards))
    return pyd_cards


@router.get("/cards/{id_card}", response_model=schemas.PydCardResponse)
def get_card(
    id_card: int,
    session_factory: sessionmaker = Depends(get_session_factory),
) -> Any:
    domain_card = crud.read_card_in_db(
        id_card=id_card,
        uow=uow.DbUnitOfWork(session_factory=session_factory),
    )
    if domain_card:
        return schemas.convert_to_pydantic(domain_card)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found.",
        )

    # item = session.get(Item, id)
    # if not item:
    #     raise HTTPException(status_code=404, detail="Item not found")
    # if not current_user.is_superuser and (item.owner_id != current_user.id):
    #     raise HTTPException(status_code=400, detail="Not enough permissions")
    # return item


@router.put("/cards/{id_card}", response_model=schemas.PydCardResponse)
def update_card(
    id_card: int,
    card_input: schemas.PydCardInput,
    session_factory: sessionmaker = Depends(get_session_factory),
) -> Any:
    domain_card = crud.update_card_in_db(
        id_card=id_card,
        **card_input.model_dump(),
        uow=uow.DbUnitOfWork(session_factory=session_factory),
    )
    if domain_card:
        return schemas.convert_to_pydantic(domain_card)
    else:
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
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found.",
        )
