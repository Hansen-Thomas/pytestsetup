from sqlalchemy import text
from sqlalchemy.orm import Session


def insert_cards(session: Session, records):
    stmt = text(
        """
        INSERT INTO Card (id, word_type, id_relevance, german, italian) 
        VALUES (:id, :word_type, :id_relevance, :german, :italian)
        """
    )
    session.execute(stmt, records)


def insert_tags(session: Session, records):
    stmt = text("INSERT INTO Tag (id, value) VALUES (:id_tag, :value)")
    session.execute(stmt, records)


def insert_associations(session: Session, records):
    stmt = text("INSERT INTO Card_has_Tag (id_card, id_tag) VALUES (:id_card, :id_tag)")
    session.execute(stmt, records)


def insert_relevance_levels(session: Session, records):
    stmt = text("INSERT INTO Relevance (id, description) VALUES (:id, :description)")
    session.execute(stmt, records)


def select_all_cards(session: Session) -> list:
    stmt = text("SELECT id, word_Type, id_relevance, german, italian FROM Card")
    return list(session.execute(stmt).all())


def select_all_tags(session: Session) -> list:
    stmt = text("SELECT id, value FROM Tag")
    return list(session.execute(stmt).all())


def select_all_card_has_tag_associations(session: Session) -> list:
    stmt = text("SELECT id_card, id_tag FROM Card_has_Tag")
    return list(session.execute(stmt).all())
