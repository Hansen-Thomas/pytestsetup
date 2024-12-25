from sqlalchemy import text
from sqlalchemy.orm import Session


def insert_cards(session: Session, records):
    stmt = text(
        "INSERT INTO Card (id, german, italian) VALUES (:id, :german, :italian)"
    )
    session.execute(stmt, records)
    session.commit()


def insert_tags(session: Session, records):
    stmt = text("INSERT INTO Tag (id, value) VALUES (:id, :value)")
    session.execute(stmt, records)
    session.commit()


def insert_associations(session: Session, records):
    stmt = text("INSERT INTO Card_has_Tag (id_card, id_tag) VALUES (:id_card, :id_tag)")
    session.execute(stmt, records)
    session.commit()
