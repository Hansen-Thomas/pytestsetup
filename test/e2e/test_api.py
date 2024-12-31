import json

from fastapi.testclient import TestClient
import pytest

from app.main import app
from database.unit_of_work import DbUnitOfWork
from domain.word_type import WordType


testclient = TestClient(app=app)


@pytest.mark.usefixtures("reset_db_for_e2e_tests")
def test_add_card_happy_path():
    # card data:
    data = {
        "word_type": WordType.VERB.value,
        "relevance_description": "A - Beginner",
        "german": "haben",
        "italian": "avere",
    }

    # add card:
    response = testclient.post(
        "/cards",
        headers={},
        json=data,
    )
    assert response.status_code == 200

    # inspect result:
    uow = DbUnitOfWork()
    with uow:
        all_cards = uow.cards.all()
        assert len(all_cards) == 1
        card = all_cards[0]
        assert card.german == "haben"
        assert card.italian == "avere"
        assert card.relevance.description == "A - Beginner"


@pytest.mark.usefixtures("reset_db_for_e2e_tests")
def test_add_card_unhappy_path_returns_400_and_error_message():
    # card data:
    data = {
        "word_type": WordType.VERB.value,
        "relevance_description": "A - Beginner",
        "german": "haben",
        "italian": "avere",
    }

    # add card:
    response = testclient.post(
        "/cards",
        headers={},
        json=data,
    )
    assert response.status_code == 200

    # add same card again:
    response = testclient.post(
        "/cards",
        headers={},
        json=data,
    )
    assert response.status_code == 400
    content = json.loads(response.content)
    assert content["detail"] == "Card already exists!"
