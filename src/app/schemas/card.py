from pydantic import BaseModel

from domain.card import Card
import app.schemas.relevance as relevance_schemas
from domain.word_type import WordType


class PydCardInput(BaseModel):
    word_type: WordType
    relevance_description: str
    german: str
    italian: str


class PydCardResponse(BaseModel):
    word_type: WordType
    relevance_description: str
    german: str
    italian: str


class PydCard(BaseModel):
    id: int | None
    word_type: WordType
    relevance: relevance_schemas.PydRelevance | None
    german: str
    italian: str


def convert_to_pydantic(card: Card) -> PydCard:
    pyd_relevance = relevance_schemas.convert_to_pydantic(card.relevance)
    return PydCard(
        id=card.id,
        word_type=card.word_type,
        relevance=pyd_relevance,
        german=card.german,
        italian=card.italian,
    )


def convert_to_domain(pyd_card: PydCard) -> Card:
    relevance = relevance_schemas.convert_to_domain(pyd_card.relevance)
    return Card(
        id=pyd_card.id,
        word_type=pyd_card.word_type,
        id_relevance=relevance.id,
        relevance=relevance,
        german=pyd_card.german,
        italian=pyd_card.italian,
    )