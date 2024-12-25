from database.repositories.card_repository import DbCardRepository
from domain.card import Card


def test_db_card_repo_can_add_card(session):
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
