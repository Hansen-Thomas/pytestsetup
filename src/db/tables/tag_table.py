from sqlalchemy import Table, Column, Integer, String

from db import metadata

tag_table = Table(
    "Tag",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("value", String, unique=True),
)
