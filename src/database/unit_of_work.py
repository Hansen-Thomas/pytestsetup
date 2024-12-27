from abc import ABC, abstractmethod
from typing import Self

from sqlalchemy.orm import Session

from database import _SessionFactory
from database.repositories.card_repository import (
    AbstractCardRepository,
    FakeCardRepository,
    DbCardRepository,
)
from database.repositories.tag_repository import (
    AbstractTagRepository,
    FakeTagRepository,
    DbTagRepository,
)


class AbstractUnitOfWork(ABC):
    cards: AbstractCardRepository
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


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.cards = FakeCardRepository(set())
        self.tags = FakeTagRepository(set())
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


class DbUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=_SessionFactory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session: Session = self.session_factory()
        self.cards = DbCardRepository(self.session)
        self.tags = DbTagRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args) -> None:
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
