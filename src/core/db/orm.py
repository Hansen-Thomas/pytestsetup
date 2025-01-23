from sqlalchemy.orm import registry, relationship

from core.domain.card import Card
from core.domain.relevance import Relevance
from core.domain.tag import Tag
from core.db.tables.card_table import card_table
from core.db.tables.relevance_table import relevance_table
from core.db.tables.tag_table import tag_table
from core.db.tables.card_has_tag_table import card_has_tag_table


mapping_registry = registry()


def start_mappers():
    if has_mappings():
        return

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
                # Don't choose "all" because of delete: "all" would include
                # delete, which would lead to the following problem:
                # If a card shall be deleted, the session would then
                # automatically cascade this delete-command as well to
                # the relevance-object that is connected to the card.
                # But we can expect that re thelevance-record in DB is as well
                # connected to other cards (normal 1:n-situation in DB).
                # Deleting the ORM-mapped relevance-object would issue
                # SQL-statements to delete the corresponding DB-record.
                # This again is very likely to not work because the DB cannot
                # violate that foreign-key-constraint as this relevance-record
                # is very likely to be connected to other cards in DB already.
                #
                # We always need to differentiate between the ORM-objects and
                # the DB-records. The cascade-parameter here deals with the
                # cascading within the ORM-object tree. The cascading in the DB
                # is defined in the SqlAlchemy-Table-objects with parameters of
                # the ForeignKey-class ("ondelete" and "onupdate"). These
                # parameters result in DDL that adds these constraints to the
                # DB-schema.
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


def has_mappings():
    """
    Is used to check if the mapping_registry already has mappings.
    """
    return bool(list(mapping_registry.mappers))
