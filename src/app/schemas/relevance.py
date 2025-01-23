from pydantic import BaseModel

from core.domain.relevance import Relevance


class PydRelevance(BaseModel):
    id: str = ""
    description: str = ""


def convert_to_pydantic(relevance: Relevance) -> PydRelevance:
    return PydRelevance(
        id=relevance.id,
        description=relevance.description,
    )


def convert_to_domain(pyd_relevance: PydRelevance) -> Relevance:
    return Relevance(
        id=pyd_relevance.id,
        description=pyd_relevance.description,
    )
