from sqlalchemy import Table, Column, String

from core.db import metadata

relevance_table = Table(
    "Relevance",
    metadata,
    Column("id", String, primary_key=True),
    Column("description", String, unique=True),
)
