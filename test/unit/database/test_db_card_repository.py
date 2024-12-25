from sqlalchemy.orm import Session, sessionmaker

from database.repositories.card_repository import DbCardRepository
from domain.card import Card
from domain.tag import Tag


def test_db_card_repo_can_add_simple_card(session: Session):
    # Arrange:
    card_repo = DbCardRepository(session)

    # Act:
    card = Card()
    card.german = "die Natur"
    card.italian = "la natura"
    card_repo.add(card)
    session.commit()

    # Assert:
    all_cards = card_repo.all()
    assert len(all_cards) == 1
    card = all_cards[0]
    assert card.german == "die Natur"


def test_db_card_repo_can_add_card_with_tags(session: Session, engine):
    # Arrange:
    card_repo = DbCardRepository(session)

    # Act:
    card = Card()
    card.german = "die Natur"
    card.italian = "la natura"
    tag1 = Tag(value="Freizeit")
    tag2 = Tag(value="Person")
    card.add_tag(tag1)
    card.add_tag(tag2)
    card_repo.add(card)
    session.commit()

    session.close()

    # Assert:
    new_session = sessionmaker(bind=engine)()
    new_repo = DbCardRepository(new_session)
    card = new_repo.get(id=1)
    assert card
    assert card.german == "die Natur"
    assert len(card.tags) == 2
    first_tag: Tag = list(card.tags)[0]
    assert first_tag.value in ("Freizeit", "Person")
    second_tag: Tag = list(card.tags)[1]
    assert second_tag.value in ("Freizeit", "Person")
