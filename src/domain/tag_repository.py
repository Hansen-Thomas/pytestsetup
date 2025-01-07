from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.tag import Tag


class AbstractTagRepository(ABC):
    @abstractmethod
    def add(self, tag: Tag) -> None:
        raise NotImplementedError

    @abstractmethod
    def all(self) -> list[Tag]:
        raise NotImplementedError

    @abstractmethod
    def get_by_value(self, value: str) -> Tag | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, tag: Tag) -> None:
        raise NotImplementedError


class FakeTagRepository(AbstractTagRepository):
    def __init__(self, tags: set[Tag]) -> None:
        self._tags = set(tags)

    def add(self, tag: Tag) -> None:
        self._tags.add(tag)

    def all(self) -> list[Tag]:
        return list(self._tags)

    def get_by_value(self, value: str) -> Tag | None:
        tag = Tag(value)
        if tag in self._tags:
            return tag
        return None

    def delete(self, tag: Tag) -> None:
        if tag in self._tags:
            self._tags.remove(tag)


class DbTagRepository(AbstractTagRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, tag: Tag) -> None:
        self.session.add(tag)

    def all(self) -> list[Tag]:
        stmt = select(Tag)
        return self.session.scalars(stmt).all()

    def get_by_value(self, value: str) -> Tag | None:
        stmt = select(Tag).where(Tag.value == value)
        return self.session.scalar(stmt)

    def delete(self, tag: Tag) -> None:
        self.session.delete(tag)
