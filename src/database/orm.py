from sqlalchemy.orm import registry

from domain.card import Card
from domain.tag import Tag
from database.tables.card_table import card_table
from database.tables.tag_table import tag_table


def start_mappers():
    mapping_registry = registry()
    mapping_registry.map_imperatively(Tag, tag_table, properties={})
    mapping_registry.map_imperatively(Card, card_table, properties={})
