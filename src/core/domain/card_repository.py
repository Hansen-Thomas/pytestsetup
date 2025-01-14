from abc import ABC, abstractmethod

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.domain.card import Card
from core.exceptions import DuplicateResourceError


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
    def get_list(self, skip: int, limit: int) -> tuple[int, list[Card]]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, card: Card) -> None:
        # Lessons learned: Parameter needs to be of type Card and not its id,
        # because in the end we definitely want to remove an instance
        # from the SqlAlchemy-Session, so it needs to be a mapped object,
        # not an integer-id. And we don't want to do the get-by-id-request
        # in this delete method.
        raise NotImplementedError


class FakeCardRepository(AbstractCardRepository):
    def __init__(self, cards: set[Card]) -> None:
        self._cards = set(cards)

    def add(self, card: Card) -> None:
        if card in self._cards:
            raise DuplicateResourceError("Card")
        self._cards.add(card)

    def all(self) -> list[Card]:
        return list(self._cards)

    def get(self, id: int) -> Card | None:
        card = [card for card in self._cards if card.id == id]
        if not card:
            return None
        return card[0]

    def get_list(self, skip: int, limit: int) -> tuple[int, list[Card]]:
        return (len(self._cards), list(self._cards))

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

    def delete(self, card: Card) -> None:
        self.session.delete(card)

    def get(self, id: int) -> Card | None:
        stmt = select(Card).where(Card.id == id)
        return self.session.scalar(stmt)

    def get_list(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[int, list[Card]]:
        count_stmt = select(func.count()).select_from(Card)
        count = self.session.scalar(count_stmt)
        count = count if count else 0

        stmt = select(Card).offset(skip).limit(limit)
        cards = self.session.scalars(stmt).all()

        return (count, list(cards))
