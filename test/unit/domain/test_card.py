from domain.card import Card
from domain.relevance import Relevance
from domain.word_type import WordType


def test_card_can_solve_guesses():
    card = Card()
    card.word_type = WordType.NOUN
    card.german = "die Antwort"
    card.italian = "la risposta"
    assert card.solve(solve_italian=True, guess="la risposta") is True
    assert card.solve(solve_italian=True, guess="la domanda") is False


def test_card_can_calculate_statistics_after_solving():
    card = Card()
    card.word_type = WordType.NOUN
    card.german = "die Antwort"
    card.italian = "la risposta"
    assert card.times_played == 0
    assert card.correct_answers == 0
    assert card.last_answer_correct is False
    assert card.last_played is None

    assert card.solve(solve_italian=True, guess="la risposta") is True
    assert card.times_played == 1
    assert card.correct_answers == 1
    assert card.wrong_answers == 0
    assert card.last_answer_correct is True
    assert card.last_played is not None

    assert card.solve(solve_italian=True, guess="la domanda") is False
    assert card.times_played == 2
    assert card.correct_answers == 1
    assert card.wrong_answers == 1
    assert card.last_answer_correct is False
    assert card.last_played is not None

    assert card.solve(solve_italian=True, guess="la risposta") is True
    assert card.times_played == 3
    assert card.correct_answers == 2
    assert card.wrong_answers == 1
    assert card.last_answer_correct is True
    assert card.last_played is not None


def test_card_can_add_and_remove_tags():
    card = Card()
    card.add_tag("tag1")
    card.add_tag("tag2")
    assert card.has_tag("tag1")
    assert card.has_tag("tag2")
    assert not card.has_tag("tag3")

    card.remove_tag("tag1")
    assert not card.has_tag("tag1")
    assert card.has_tag("tag2")

    card.remove_tag("tag2")
    assert not card.has_tag("tag2")


def test_card_equality():
    relevance_A = Relevance(name="A-Level")
    relevance_B = Relevance(name="B-Level")

    card_1 = Card(
        word_type=WordType.NOUN,
        relevance=relevance_A,
        german="das Haus",
        italian="la casa",
    )

    # assert totally equal card is equal:
    totally_equal_card = Card(
        word_type=WordType.NOUN,
        relevance=relevance_A,
        german="das Haus",
        italian="la casa",
    )
    assert card_1 == totally_equal_card

    # assert card for totally different word is not equal:
    card_2 = Card(
        word_type=WordType.NOUN,
        relevance=relevance_A,
        german="der Baum",
        italian="l'albero",
    )
    assert card_1 != card_2

    # assert card with same word is equal even if word_type or relevance are 
    # different:
    card_3 = Card(
        word_type=WordType.ADJECTIVE,
        relevance=relevance_A,
        german="das Haus",
        italian="la casa",
    )
    assert card_1 == card_3

    card_4 = Card(
        word_type=WordType.NOUN,
        relevance=relevance_B,
        german="das Haus",
        italian="la casa",
    )
    assert card_1 == card_4

    # assert cards are not equal if one of both languages is different:
    card_5 = Card(
        word_type=WordType.NOUN,
        relevance=relevance_A,
        german="das Appartment",
        italian="la casa",
    )
    assert card_1 != card_5

    card_6 = Card(
        word_type=WordType.NOUN,
        relevance=relevance_A,
        german="das Haus",
        italian="il palazzo",
    )
    assert card_1 != card_6
