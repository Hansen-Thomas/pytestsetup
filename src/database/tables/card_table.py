from sqlalchemy import Table, Column, Integer, String

from database import metadata

card_table = Table(
    "Card",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("german", String),
    Column("italian", String),
)
