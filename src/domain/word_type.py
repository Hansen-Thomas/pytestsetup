from enum import Enum


class WordType(Enum):
    NONE = "NONE"
    NOUN = "NOUN"
    VERB = "VERB"
    ADJECTIVE = "ADJECTIVE"
    ADVERB = "ADVERB"
    PRONOUN = "PRONOUN"
    PREPOSITION = "PREPOSITION"

    @classmethod
    def all(cls) -> list[str]:
        return sorted(cls._member_names_)
