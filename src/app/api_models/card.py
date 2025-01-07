from pydantic import BaseModel

from domain.card import Card
import app.api_models.relevance as relevance_models
from domain.word_type import WordType


class PydCardInputModel(BaseModel):
    word_type: WordType
    relevance_description: str
    german: str
    italian: str


class PydCardModel(BaseModel):
    id: int | None
    word_type: WordType
    relevance: relevance_models.PydRelevanceModel | None
    german: str
    italian: str


def convert_to_pydantic(card: Card) -> PydCardModel:
    pyd_relevance = relevance_models.convert_to_pydantic(card.relevance)
    return PydCardModel(
        id=card.id,
        word_type=card.word_type,
        relevance=pyd_relevance,
        german=card.german,
        italian=card.italian,
    )


def convert_to_domain(pyd_card: PydCardModel) -> Card:
    relevance = relevance_models.convert_to_domain(pyd_card.relevance)
    return Card(
        id=pyd_card.id,
        word_type=pyd_card.word_type,
        id_relevance=relevance.id,
        relevance=relevance,
        german=pyd_card.german,
        italian=pyd_card.italian,
    )
