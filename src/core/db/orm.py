from sqlalchemy.orm import registry, relationship

from core.domain.card import Card
from core.domain.relevance import Relevance
from core.domain.tag import Tag
from core.db.tables.card_table import card_table
from core.db.tables.relevance_table import relevance_table
from core.db.tables.tag_table import tag_table
from core.db.tables.card_has_tag_table import card_has_tag_table


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
                cascade="save-update, expunge",
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
