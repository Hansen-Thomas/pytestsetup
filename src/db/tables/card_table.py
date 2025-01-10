from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)

from db import metadata
from domain.word_type import WordType

card_table = Table(
    "Card",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("word_type", Enum(WordType)),
    Column("id_relevance", ForeignKey("Relevance.id")),
    Column("german", String, nullable=False),
    Column("italian", String, nullable=False),
    UniqueConstraint("german", "italian", name="uq_german_italian"),
)
