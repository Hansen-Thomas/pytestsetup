from fastapi.testclient import TestClient

from services.unit_of_work import DbUnitOfWork
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
    assert response.status_code == 201

    # inspect result:
    uow = DbUnitOfWork(session_factory=session_factory)
    with uow:
        all_cards = uow.cards.all()
        assert len(all_cards) == 1
        card = all_cards[0]
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
    assert response.status_code == 201

    # add same card again:
    response = client.post(
        "/cards",
        headers={},
        json=data,
    )
    assert response.status_code == 400


def test_get_card_happy_path(client: TestClient, session_factory):
    # arrange:
    data_1 = {
        "word_type": WordType.VERB.value,
        "relevance_description": "A - Beginner",
        "german": "haben",
        "italian": "avere",
    }
    response = client.post(
        "/cards",
        headers={},
        json=data_1,
    )
    assert response.status_code == 201

    data_2 = {
        "word_type": WordType.ADJECTIVE.value,
        "relevance_description": "A - Beginner",
        "german": "alt",
        "italian": "vecchio",
    }
    response = client.post(
        "/cards",
        headers={},
        json=data_2,
    )
    assert response.status_code == 201

    # act:
    response = client.get("/cards/2")

    # assert:
    assert response.status_code == 200
    data = response.json()
    assert data["italian"] == "vecchio"


def test_get_all_cards_happy_path(client: TestClient, session_factory):
    # arrange:
    data_1 = {
        "word_type": WordType.VERB.value,
        "relevance_description": "A - Beginner",
        "german": "haben",
        "italian": "avere",
    }
    response = client.post(
        "/cards",
        headers={},
        json=data_1,
    )
    assert response.status_code == 201

    data_2 = {
        "word_type": WordType.ADJECTIVE.value,
        "relevance_description": "A - Beginner",
        "german": "alt",
        "italian": "vecchio",
    }
    response = client.post(
        "/cards",
        headers={},
        json=data_2,
    )
    assert response.status_code == 201

    # act:
    response = client.get("/cards")

    # assert:
    assert response.status_code == 200
    data = response.json()
    assert data


def test_update_card_happy_path(client: TestClient, session_factory):
    # wrong card data:
    data = {
        "word_type": WordType.ADJECTIVE.value,  # wrong, needs to be corrected
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
    assert response.status_code == 201

    corrected_data = {
        "word_type": WordType.VERB.value,  # updated
        "relevance_description": "A - Beginner",
        "german": "haben",
        "italian": "avere",
    }

    # update card:
    response = client.put(
        "/cards/1",
        headers={},
        json=corrected_data,
    )
    assert response.status_code == 200

    # instpect result:
    uow = DbUnitOfWork(session_factory=session_factory)
    with uow:
        all_cards = uow.cards.all()
        assert len(all_cards) == 1
        card = all_cards[0]
        assert card.word_type == WordType.VERB
        assert card.german == "haben"
        assert card.italian == "avere"
        assert card.relevance.description == "A - Beginner"


def test_update_card_unhappy_path_returns_404_when_card_not_found(
    client: TestClient,
):
    # wrong card data:
    data = {
        "word_type": WordType.ADJECTIVE.value,  # wrong, needs to be corrected
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
    assert response.status_code == 201

    corrected_data = {
        "word_type": WordType.VERB.value,  # updated
        "relevance_description": "A - Beginner",
        "german": "haben",
        "italian": "avere",
    }

    # update card:
    response = client.put(
        "/cards/2",  # wrong id (should be 1)
        headers={},
        json=corrected_data,
    )
    assert response.status_code == 404


def test_delete_card_happy_path(client: TestClient, session_factory):
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
    assert response.status_code == 201

    uow = DbUnitOfWork(session_factory=session_factory)
    with uow:
        all_cards = uow.cards.all()
        assert all_cards

    # delete card:
    response = client.delete(
        "/cards/1",
        headers={},
    )
    assert response.status_code == 204

    # inspect result:
    with uow:
        all_cards = uow.cards.all()
        assert not all_cards


def test_delete_card_unhappy_path_returns_404_when_card_not_found(
    client: TestClient, session_factory
):
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
    assert response.status_code == 201

    uow = DbUnitOfWork(session_factory=session_factory)
    with uow:
        all_cards = uow.cards.all()
        assert all_cards

    # delete card:
    response = client.delete(
        "/cards/2",  # does not exist
        headers={},
    )
    assert response.status_code == 404

    # inspect result:
    with uow:
        all_cards = uow.cards.all()
        assert all_cards
