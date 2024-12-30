from sqlalchemy import Table, Column, Integer, String

from database import metadata

relevance_table = Table(
    "Relevance",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("description", String, unique=True),
)
