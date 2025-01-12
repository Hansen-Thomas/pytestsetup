from abc import ABC, abstractmethod
from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from domain.card_repository import (
    AbstractCardRepository,
    FakeCardRepository,
    DbCardRepository,
)
from domain.relevance_repository import (
    AbstractRelevanceRepository,
    FakeRelevanceRepository,
    DbRelevanceRepository,
)
from domain.tag_repository import (
    AbstractTagRepository,
    FakeTagRepository,
    DbTagRepository,
)


class AbstractUnitOfWork(ABC):
    session: Session
    cards: AbstractCardRepository
    relevance_levels: AbstractRelevanceRepository
    tags: AbstractTagRepository

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self.rollback()

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def refresh(self, instance) -> None:
        raise NotImplementedError

    @abstractmethod
    def expunge(self, instance) -> None:
        raise NotImplementedError

    @abstractmethod
    def expunge_all(self) -> None:
        raise NotImplementedError


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.cards = FakeCardRepository(set())
        self.relevance_levels = FakeRelevanceRepository(set())
        self.tags = FakeTagRepository(set())
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass

    def refresh(self, instance) -> None:
        pass

    def expunge(self, instance) -> None:
        pass

    def expunge_all(self) -> None:
        pass


class DbUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        session_factory: sessionmaker,
        session_shall_expire_on_commit: bool = True,
    ):
        """The session_factory decides which database to use."""
        self.session_factory = session_factory
        self.session_shall_expire_on_commit = session_shall_expire_on_commit

    def __enter__(self):
        self.session = self.session_factory()
        self.session.expire_on_commit = self.session_shall_expire_on_commit

        self.cards = DbCardRepository(self.session)
        self.relevance_levels = DbRelevanceRepository(self.session)
        self.tags = DbTagRepository(self.session)

        return super().__enter__()

    def __exit__(self, *args) -> None:
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, instance) -> None:
        self.session.refresh(instance)

    def expunge(self, instance) -> None:
        self.session.expunge(instance)

    def expunge_all(self) -> None:
        self.session.expunge_all()
