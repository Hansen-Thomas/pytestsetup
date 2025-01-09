from domain.card import Card
# from domain.word_type import WordType


def get_card1() -> Card:
    card = Card()
    # card.word_type = WordType.NOUN
    card.german = "die Antwort"
    card.italian = "la risposta"
    return card


def get_card2() -> Card:
    card = Card()
    # card.word_type = WordType.NOUN
    card.german = "die Frage"
    card.italian = "la domanda"
    return card


def get_card3() -> Card:
    card = Card()
    # card.word_type = WordType.NOUN
    card.german = "die Katze"
    card.italian = "il gatto"
    return card


def get_card4() -> Card:
    card = Card()
    # card.word_type = WordType.VERB
    card.german = "gehen"
    card.italian = "andare"
    return card


def get_card5() -> Card:
    card = Card()
    # card.word_type = WordType.VERB
    card.german = "haben"
    card.italian = "avere"
    return card


def get_cards_for_testing() -> list[Card]:
    card1 = get_card1()
    card2 = get_card2()
    card3 = get_card3()
    card4 = get_card4()
    card5 = get_card5()
    return [card1, card2, card3, card4, card5]
