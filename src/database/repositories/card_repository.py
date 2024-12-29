from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.card import Card


class DuplicateCardException(Exception):
    def __init__(self, message="Duplicate card found"):
        self.message = message
        super().__init__(self.message)


class AbstractCardRepository(ABC):
    @abstractmethod
    def add(self, card: Card) -> None:
        raise NotImplementedError

    @abstractmethod
    def all(self) -> list[Card]:
        raise NotImplementedError

    @abstractmethod
    def get(self, id: int) -> Card | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, card: Card) -> None:
        raise NotImplementedError


class FakeCardRepository(AbstractCardRepository):
    def __init__(self, cards: set[Card]) -> None:
        self._cards = set(cards)

    def add(self, card: Card) -> None:
        if card in self._cards:
            raise DuplicateCardException()
        self._cards.add(card)

    def all(self) -> list[Card]:
        return list(self._cards)

    def get(self, id: int) -> Card | None:
        card = Card()
        card.id = id
        if card in self._cards:
            return card
        return None

    def delete(self, card: Card) -> None:
        if card in self._cards:
            self._cards.remove(card)


class DbCardRepository(AbstractCardRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, card: Card) -> None:
        self.session.add(card)

    def all(self) -> list[Card]:
        stmt = select(Card)
        return list(self.session.scalars(stmt).all())

    def get(self, id: int) -> Card | None:
        stmt = select(Card).where(Card.id == id)
        return self.session.scalar(stmt)

    def delete(self, card: Card) -> None:
        self.session.delete(card)
