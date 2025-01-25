from abc import ABC, abstractmethod
import logging
from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from core.domain.card_repository import (
    AbstractCardRepository,
    FakeCardRepository,
    DbCardRepository,
)
from core.domain.relevance_repository import (
    AbstractRelevanceRepository,
    FakeRelevanceRepository,
    DbRelevanceRepository,
)
from core.domain.tag_repository import (
    AbstractTagRepository,
    FakeTagRepository,
    DbTagRepository,
)


logger = logging.getLogger(__name__)


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
        logger.debug("DB UOW: Entered, start session.")
        self.session = self.session_factory()
        self.session.expire_on_commit = self.session_shall_expire_on_commit

        self.cards = DbCardRepository(self.session)
        self.relevance_levels = DbRelevanceRepository(self.session)
        self.tags = DbTagRepository(self.session)

        return super().__enter__()

    def __exit__(self, *args) -> None:
        super().__exit__(*args)
        self.session.close()
        logger.debug("DB UOW: Exited, session closed.")
        engine = self.session.get_bind()
        logger.debug(f"Status connection-pool: {engine.pool.status()}")

    def commit(self) -> None:
        self.session.commit()
        logger.debug("DB UOW: Session committed.")

    def rollback(self) -> None:
        self.session.rollback()
        logger.debug("DB UOW: Session rolled back.")

    def refresh(self, instance) -> None:
        self.session.refresh(instance)

    def expunge(self, instance) -> None:
        self.session.expunge(instance)

    def expunge_all(self) -> None:
        self.session.expunge_all()
