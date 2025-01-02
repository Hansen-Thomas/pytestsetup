from fastapi.testclient import TestClient

from database.unit_of_work import DbUnitOfWork
from domain.word_type import WordType


def test_add_card_happy_path(client: TestClient, session_factory):
    # card data:
    data = {
        "word_type": WordType.VERB.value,
        "relevance_description": "A - Beginner",
        "german": "haben",
        "italian": "avere",
    }

    # add card:
    response = client.post(
        "/cards",
        headers={},
        json=data,
    )
    assert response.status_code == 200

    # inspect result:
    uow = DbUnitOfWork(session_factory=session_factory)
    with uow:
        all_cards = uow.cards.all()
        assert len(all_cards) == 1
        card = all_cards[0]
        assert False
        assert card.german == "haben"
        assert card.italian == "avere"
        assert card.relevance.description == "A - Beginner"


def test_add_card_unhappy_path_returns_400_and_error_message(client: TestClient):
    # card data:
    data = {
        "word_type": WordType.VERB.value,
        "relevance_description": "A - Beginner",
        "german": "haben",
        "italian": "avere",
    }

    # add card:
    response = client.post(
        "/cards",
        headers={},
        json=data,
    )
    assert response.status_code == 200

    # add same card again:
    response = client.post(
        "/cards",
        headers={},
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Card already exists!"
