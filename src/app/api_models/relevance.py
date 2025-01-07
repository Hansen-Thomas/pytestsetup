from pydantic import BaseModel

from domain.relevance import Relevance


class PydRelevanceModel(BaseModel):
    id: int | None = None
    description: str = ""


def convert_to_pydantic(relevance: Relevance | None) -> PydRelevanceModel:
    if relevance:
        return PydRelevanceModel(
            id=relevance.id,
            description=relevance.description,
        )
    else:
        return PydRelevanceModel()


def convert_to_domain(pyd_relevance: PydRelevanceModel | None) -> Relevance:
    if pyd_relevance:
        return Relevance(
            id=pyd_relevance.id,
            description=pyd_relevance.description,
        )
    else:
        return Relevance()
