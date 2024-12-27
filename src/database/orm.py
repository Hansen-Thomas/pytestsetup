from sqlalchemy.orm import registry, relationship

from domain.card import Card
from domain.relevance import Relevance
from domain.tag import Tag
from database.tables.card_table import card_table
from database.tables.relevance_table import relevance_table
from database.tables.tag_table import tag_table
from database.tables.card_has_tag_table import card_has_tag_table


def start_mappers():
    mapping_registry = registry()
    mapping_registry.map_imperatively(
        Card,
        card_table,
        properties={
            "tags": relationship(
                Tag,
                secondary=card_has_tag_table,
                collection_class=set,
                lazy="immediate",
                cascade="all",
            ),
            "relevance": relationship(
                Relevance,
                lazy="immediate",
                cascade="all",
            ),
        },
    )
    mapping_registry.map_imperatively(
        Tag,
        tag_table,
        properties={},
        confirm_deleted_rows=False,
    )
    mapping_registry.map_imperatively(
        Relevance,
        relevance_table,
        properties={},
    )
