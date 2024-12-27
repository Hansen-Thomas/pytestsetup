from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.card import Card
from domain.tag import Tag
import test.integration.integration_utils as plain_sql_utils


def test_session_can_load_cards(session: Session):
    # Arrange:
    records = [
        {"id": 1, "german": "das Haus", "italian": "la casa"},
        {"id": 2, "german": "der Baum", "italian": "l'albero"},
    ]
    plain_sql_utils.insert_cards(session=session, records=records)
    session.commit()

    # Act:
    orm_stmt_select = select(Card)
    result = session.scalars(orm_stmt_select).all()

    # Assert:
    expected = [
        Card(id=1, german="das Haus", italian="la casa"),
        Card(id=2, german="der Baum", italian="l'albero"),
    ]
    assert result == expected


def test_session_can_load_tags(session: Session):
    # Arrange:
    records = [
        {"id": 7, "value": "Urlaub"},
        {"id": 8, "value": "Arbeit"},
    ]
    plain_sql_utils.insert_tags(session=session, records=records)
    session.commit()

    # Act:
    orm_stmt_select = select(Tag)
    result = session.scalars(orm_stmt_select).all()

    # Assert:
    expected = [
        Tag(id=7, value="Urlaub"),
        Tag(id=8, value="Arbeit"),
    ]
    assert result == expected


def test_session_can_load_card_has_tag_association(session: Session):
    # Arrange:
    records_cards = [
        {"id": 1, "german": "das Haus", "italian": "la casa"},
        {"id": 2, "german": "der Baum", "italian": "l'albero"},
    ]
    plain_sql_utils.insert_cards(session=session, records=records_cards)
    session.commit()

    records_tags = [
        {"id": 7, "value": "Urlaub"},
        {"id": 8, "value": "Arbeit"},
    ]
    plain_sql_utils.insert_tags(session=session, records=records_tags)
    session.commit()

    records_association = [
        {"id_card": 1, "id_tag": 7},
        {"id_card": 1, "id_tag": 8},
        {"id_card": 2, "id_tag": 7},
    ]
    plain_sql_utils.insert_associations(session=session, records=records_association)
    session.commit()

    # Act:
    orm_stmt_select = select(Card)
    result = session.scalars(orm_stmt_select).all()

    # Assert:
    expected_card1 = Card(id=1, german="das Haus", italian="la casa")
    expected_tags_card1 = ["Urlaub", "Arbeit"]

    expected_card2 = Card(id=2, german="der Baum", italian="l'albero")
    expected_tags_card2 = ["Urlaub"]

    expected = [expected_card1, expected_card2]
    for card in result:
        assert card in expected
        if card.id == 1:
            expected_tags = expected_tags_card1
        else:
            expected_tags = expected_tags_card2
        for tag in expected_tags:
            assert card.has_tag(tag)


def test_session_can_save_cards(session: Session):
    # Arrange:
    cards_to_insert = [
        Card(german="gehen", italian="andare"),
        Card(german="fliegen", italian="volare"),
    ]
    session.add_all(cards_to_insert)
    session.commit()

    # Act:
    result = plain_sql_utils.select_all_cards(session=session)

    # Assert:
    expected = [
        (1, "gehen", "andare"),
        (2, "fliegen", "volare"),
    ]
    for row in result:
        assert row in expected


def test_session_can_save_tags(session: Session):
    # Arrange:
    tags_to_insert = [
        Tag(value="Zuhause"),
        Tag(value="Verkehr"),
    ]
    session.add_all(tags_to_insert)
    session.commit()

    # Act:
    result = plain_sql_utils.select_all_tags(session=session)

    # Assert:
    expected = [(1, "Zuhause"), (2, "Verkehr")]
    for row in result:
        assert row in expected


def test_session_can_save_card_has_tag_associations(session: Session):
    # Arrange:
    card = Card(german="das Flugzeug", italian="l'aereo")
    card.add_tag("Verkehr")
    card.add_tag("Beruf")
    session.add(card)
    session.commit()

    # Act:
    result_card = plain_sql_utils.select_all_cards(session=session)[0]
    result_tag = plain_sql_utils.select_all_tags(session=session)
    result_association = plain_sql_utils.select_all_card_has_tag_associations(
        session=session
    )

    # Assert:
    expected_card_data = (1, "das Flugzeug", "l'aereo")
    expected_tag_values = ["Verkehr", "Beruf"]
    expected_associations = [(1, 1), (1, 2)]
    assert result_card == expected_card_data
    for tag in result_tag:
        (id, value) = tag
        assert value in expected_tag_values
    for association in result_association:
        assert association in expected_associations
