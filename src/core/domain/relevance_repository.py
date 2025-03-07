from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.domain.relevance import Relevance


class AbstractRelevanceRepository(ABC):
    @abstractmethod
    def add(self, relevance: Relevance) -> None:
        raise NotImplementedError

    @abstractmethod
    def all(self) -> list[Relevance]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str) -> Relevance | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, relevance: Relevance) -> None:
        raise NotImplementedError


class FakeRelevanceRepository(AbstractRelevanceRepository):
    def __init__(self, relevance_levels: set[Relevance]) -> None:
        self._relevance_levels = set(relevance_levels)

    def add(self, relevance: Relevance) -> None:
        self._relevance_levels.add(relevance)

    def all(self) -> list[Relevance]:
        return list(self._relevance_levels)

    def get_by_id(self, id: str) -> Relevance | None:
        relevance = [r for r in self._relevance_levels if r.id == id]
        if relevance:
            return relevance[0]
        return None

    def delete(self, relevance: Relevance) -> None:
        if relevance in self._relevance_levels:
            self._relevance_levels.remove(relevance)


class DbRelevanceRepository(AbstractRelevanceRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, relevance: Relevance) -> None:
        self.session.add(relevance)

    def all(self) -> list[Relevance]:
        stmt = select(Relevance)
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, id: str) -> Relevance | None:
        stmt = select(Relevance).where(Relevance.id == id)
        return self.session.scalar(stmt)

    def delete(self, relevance: Relevance) -> None:
        self.session.delete(relevance)
