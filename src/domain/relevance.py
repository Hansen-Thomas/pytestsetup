from typing import Self


class Relevance:
    def __init__(self, id: int | None = None, name: str = ""):
        self.id = id
        self.name = name

    def __eq__(self, other: Self) -> bool:
        if other is None:
            return False
        elif not isinstance(other, Relevance):
            return False
        else:
            return self.name == other.name

    def __repr__(self) -> str:
        return (
            "Relevance("
            f"id={self.id}, "
            f"name={self.name}"
            ")"
        )