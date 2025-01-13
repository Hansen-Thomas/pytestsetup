from pydantic import BaseModel

from core.domain.relevance import Relevance


class PydRelevance(BaseModel):
    id: int | None = None
    description: str = ""


def convert_to_pydantic(relevance: Relevance | None) -> PydRelevance:
    if relevance:
        return PydRelevance(
            id=relevance.id,
            description=relevance.description,
        )
    else:
        return PydRelevance()


def convert_to_domain(pyd_relevance: PydRelevance | None) -> Relevance:
    if pyd_relevance:
        return Relevance(
            id=pyd_relevance.id,
            description=pyd_relevance.description,
        )
    else:
        return Relevance()
