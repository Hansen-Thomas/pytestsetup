from pydantic import BaseModel

from domain.relevance import Relevance


class RelevanceModel(BaseModel):  # (DTO)
    id: int | None = None
    description: str = ""


def convert_to_pydantic(relevance: Relevance | None) -> RelevanceModel:
    if relevance:
        return RelevanceModel(
            id=relevance.id,
            description=relevance.description,
        )
    else:
        return RelevanceModel()


def convert_to_domain(pyd_relevance: RelevanceModel | None) -> Relevance:
    if pyd_relevance:
        return Relevance(
            id=pyd_relevance.id,
            description=pyd_relevance.description,
        )
    else:
        return Relevance()
