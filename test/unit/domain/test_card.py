from domain.card import Card


def test_card_can_be_created():
    card = Card()
    card.german = "bla"
    card.italian = "blubb"
    assert card.german == "bla"
