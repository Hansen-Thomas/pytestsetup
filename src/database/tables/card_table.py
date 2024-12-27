from sqlalchemy import Table, Column, Enum, Integer, String

from database import metadata
from domain.word_type import WordType

card_table = Table(
    "Card",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("word_type", Enum(WordType)),
    Column("german", String),
    Column("italian", String),
)
