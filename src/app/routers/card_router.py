from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.dependencies import get_session_factory
import app.schemas.card as card_schemas
from app.templates import templates
from core.domain.word_type import WordType
import core.exceptions as exc
import core.services.cards.crud as crud
import core.services.unit_of_work as uow


router = APIRouter()


@router.post(
    "/cards",
    response_model=card_schemas.PydCardResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_card(
    request: Request,
    session_factory=Depends(get_session_factory),
) -> Any:
    
    # manually validate input depending on content-type:
    if request.headers.get("content-type") == "application/json":
        # get data from JSON-body:
        input_data = await request.json()
    else:
        # get data from forms-body:
        input_data = await request.form()
    card_input = card_schemas.PydCardInput(**input_data)

    try:
        # add card:
        new_domain_card = crud.create_card_in_db(
            **card_input.model_dump(),
            uow=uow.DbUnitOfWork(session_factory=session_factory),
        )
        # create response:
        accept = request.headers.get("accept")
        if accept and "text/html" in accept:
            return RedirectResponse(url="/cards", status_code=303)
            # (change status-code to change from POST- to GET-request.)
        else:
            return card_schemas.convert_to_pydantic(new_domain_card)
    except exc.DuplicateResourceError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card already exists.",
        )
    

@router.get("/cards", response_model=list[card_schemas.PydCardResponse])
def read_cards(
    request: Request,
    session_factory=Depends(get_session_factory),
    page: int = 1,
    page_size: int = 100,
) -> Any:
    """
    read_cards always works with pagination!
    """
    result = crud.read_cards_from_db(
        uow=uow.DbUnitOfWork(session_factory=session_factory),
        page=page,
        page_size=page_size,
    )

    accept = request.headers.get("accept")
    if accept and "text/html" in accept:
        return templates.TemplateResponse(
            request=request,
            name="cards/cards.html",
            context={
                "pagination_result": result,
            },
        )
    else:
        result.serialize_records(card_schemas.convert_to_pydantic)
        return result.records


@router.get("/cards/new")
def new_card(request: Request):
    accept = request.headers.get("accept")
    if accept and "text/html" in accept:
        return templates.TemplateResponse(
            request=request,
            name="cards/new_card.html",
            context={"word_type_enum": WordType}
        )


@router.get("/cards/{id_card}", response_model=card_schemas.PydCardResponse)
def read_card(
    id_card: int,
    session_factory=Depends(get_session_factory),
) -> Any:
    try:
        domain_card = crud.read_card_from_db(
            id_card=id_card,
            uow=uow.DbUnitOfWork(session_factory=session_factory),
        )
        return card_schemas.convert_to_pydantic(domain_card)
    except exc.ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found.",
        )


@router.put("/cards/{id_card}", response_model=card_schemas.PydCardResponse)
def update_card(
    id_card: int,
    card_input: card_schemas.PydCardInput,
    session_factory=Depends(get_session_factory),
) -> Any:
    try:
        updated_domain_card = crud.update_card_in_db(
            id_card=id_card,
            **card_input.model_dump(),
            uow=uow.DbUnitOfWork(session_factory=session_factory),
        )
        return card_schemas.convert_to_pydantic(updated_domain_card)
    except exc.ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found.",
        )


@router.delete("/cards/{id_card}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    id_card: int,
    session_factory=Depends(get_session_factory),
):
    try:
        crud.delete_card_in_db(
            id_card=id_card,
            uow=uow.DbUnitOfWork(session_factory=session_factory),
        )
    except exc.ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found.",
        )
