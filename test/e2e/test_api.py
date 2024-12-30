from fastapi.testclient import TestClient
import pytest

from app.main import app
from database.unit_of_work import DbUnitOfWork
from domain.word_type import WordType


testclient = TestClient(app=app)


@pytest.mark.usefixtures("reset_db")
def test_add_card_happy_path():
    word_type = WordType.VERB
    relevance_description = "A - Beginner"
    german = "haben"
    italian = "avere"

    response = testclient.post(
        "/cards",
        headers={},
        json={
            "word_type": word_type.value,
            "relevance_description": relevance_description,
            "german": german,
            "italian": italian,
        },
    )
    assert response.status_code == 200

    uow = DbUnitOfWork()
    with uow:
        all_cards = uow.cards.all()
        assert len(all_cards) == 1
        card = all_cards[0]
        assert card.german == "haben"
        assert card.italian == "avere"



# def test_unhappy_path_returns_400_and_error_message():
#     unknown_sku, orderid = random_sku(), random_orderid()
#     data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}
#     url = config.get_api_url()
#     r = requests.post(f"{url}/allocate", json=data)
#     assert r.status_code == 400
#     assert r.json()["message"] == f"Invalid sku {unknown_sku}"
