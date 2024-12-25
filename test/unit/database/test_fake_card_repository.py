from database.repositories.card_repository import FakeCardRepository
from domain.card import Card


def test_fake_card_repo_can_add_card(fake_session):
    # Arrange:
    card_repo = FakeCardRepository(fake_session)

    # Act:
    card = Card()
    card.german = "die Natur"
    card.italian = "la natura"
    card_repo.add(card)
    fake_session.commit()

    # Assert:
    all_cards = card_repo.all()
    assert len(all_cards) == 1
    card = all_cards[0]
    assert card.german == "die Natur"
