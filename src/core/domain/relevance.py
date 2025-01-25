class Relevance:
    def __init__(self, id: str, description: str = ""):
        self.id = id
        self.description = description

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False
        elif not isinstance(other, Relevance):
            return False
        else:
            return self.id == other.id

    def __repr__(self) -> str:
        return (
            "Relevance("
            f"id={self.id}, "
            f"description={self.description}"
            ")"
        )