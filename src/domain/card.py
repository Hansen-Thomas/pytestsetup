import datetime

from domain.relevance import Relevance
from domain.tag import Tag
from domain.word_type import WordType


class Card:
    def __init__(
        self,
        id: int | None = None,
        word_type: WordType = WordType.NONE,
        id_relevance: int | None = None,
        relevance: Relevance | None = None,
        german: str = "",
        italian: str = "",
    ):
        self.id = id
        self.word_type = word_type  # example for enum-type-member
        self.id_relevance = id_relevance  # foreign-key of 1:n-relation
        self.relevance = relevance  # relation-object
        self.german = german
        self.italian = italian

        self.tags: set[Tag] = set()

        self.times_played: int = 0
        self.correct_answers: int = 0
        self.last_answer_correct: bool = False
        self.last_played: datetime.datetime | None = None

    def __repr__(self) -> str:
        return (
            "Card("
            f"id={self.id}, "
            f"word_type={self.word_type}, "
            f"id_relevance={self.id_relevance}, "
            f"relevance={self.relevance}, "
            f"german={self.german}, "
            f"italian={self.italian}"
            ")"
        )

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False
        elif not isinstance(other, Card):
            return False
        else:
            return (
                self.german == other.german
                and self.italian == other.italian
            )

    def __hash__(self) -> int:
        return hash(self.id)

    def solve(self, solve_italian: bool, guess: str) -> bool:
        if solve_italian:
            solution = self.italian
        else:
            solution = self.german
        correct = True if guess == solution else False
        self.update_statistics(correct=correct)
        return correct

    def update_statistics(self, correct: bool) -> None:
        self.times_played += 1
        if correct:
            self.correct_answers += 1
        self.last_answer_correct = correct
        self.last_played = datetime.datetime.now()

    @property
    def wrong_answers(self):
        return self.times_played - self.correct_answers

    def add_tag(self, value: str):
        tag = Tag(value=value)
        self.tags.add(tag)

    def remove_tag(self, value: str):
        tag = Tag(value=value)
        if tag in self.tags:
            self.tags.remove(tag)

    def has_tag(self, value: str) -> bool:
        tag = Tag(value=value)
        return tag in self.tags
