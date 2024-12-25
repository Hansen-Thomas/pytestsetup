from sqlalchemy import Table, Column, Integer, ForeignKey

from database import metadata

card_has_tag_table = Table(
    "Card_has_Tag",
    metadata,
    Column(
        "id_card",
        Integer,
        ForeignKey("Card.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_tag",
        Integer,
        ForeignKey("Tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
