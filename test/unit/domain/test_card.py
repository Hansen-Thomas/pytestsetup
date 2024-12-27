from domain.card import Card
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
