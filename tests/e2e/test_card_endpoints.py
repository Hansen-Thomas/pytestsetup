from fastapi.testclient import TestClient

from core.services.unit_of_work import DbUnitOfWork
from core.domain.word_type import WordType
from core.domain.card import Card
from core.domain.relevance import Relevance


def test_create_card_happy_path(client: TestClient, session_factory):
    # card data:
    data = {
        "word_type": WordType.VERB.value,
        "relevance_id": "A",
        "relevance_description": "Beginner",
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
        assert card.relevance.description == "Beginner"


def test_create_card_unhappy_path_returns_400_and_error_message(client: TestClient):
    # card data:
    data = {
        "word_type": WordType.VERB.value,
        "relevance_id": "A",
        "relevance_description": "Beginner",
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


def test_read_card_happy_path(client: TestClient, session_factory):
    # arrange:
    with session_factory() as session:
        relevance = Relevance(id="A", description="Beginner")
        card_1 = Card(
            word_type=WordType.VERB,
            relevance=relevance,
            german="haben",
            italian="avere",
        )
        card_2 = Card(
            word_type=WordType.ADJECTIVE,
            relevance=relevance,
            german="alt",
            italian="vecchio",
        )
        session.add(card_1)
        session.add(card_2)
        session.commit()

    # act:
    response = client.get("/cards/2")

    # assert:
    assert response.status_code == 200
    data = response.json()
    assert data["italian"] == "vecchio"


def test_read_card_unhappy_path_throws_404(client: TestClient, session_factory):
    # arrange:
    with session_factory() as session:
        relevance = Relevance(id="A", description="Beginner")
        card_1 = Card(
            word_type=WordType.VERB,
            relevance=relevance,
            german="haben",
            italian="avere",
        )
        card_2 = Card(
            word_type=WordType.ADJECTIVE,
            relevance=relevance,
            german="alt",
            italian="vecchio",
        )
        session.add(card_1)
        session.add(card_2)
        session.commit()

    # act:
    response = client.get("/cards/3")  # id=3 does not exist!

    # assert:
    assert response.status_code == 404


def test_read_cards_happy_path(client: TestClient, session_factory):
    # arrange:
    with session_factory() as session:
        relevance = Relevance(id="A", description="Beginner")
        card_1 = Card(
            word_type=WordType.VERB,
            relevance=relevance,
            german="haben",
            italian="avere",
        )
        card_2 = Card(
            word_type=WordType.ADJECTIVE,
            relevance=relevance,
            german="alt",
            italian="vecchio",
        )
        session.add(card_1)
        session.add(card_2)
        session.commit()

    # act:
    response = client.get("/cards")

    # assert:
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_read_cards_pagination(client: TestClient, session_factory):
    # arrange:
    with session_factory() as session:
        relevance = Relevance(id="A", description="Beginner")
        card_1 = Card(
            word_type=WordType.VERB,
            relevance=relevance,
            german="haben",
            italian="avere",
        )
        card_2 = Card(
            word_type=WordType.ADJECTIVE,
            relevance=relevance,
            german="alt",
            italian="vecchio",
        )
        card_3 = Card(
            word_type=WordType.NOUN,
            relevance=relevance,
            german="das Haus",
            italian="la casa",
        )
        session.add(card_1)
        session.add(card_2)
        session.add(card_3)
        session.commit()

    # act:
    response = client.get("/cards?page=2&page_size=2")

    # assert:
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["german"] == "das Haus"


def test_update_card_happy_path(client: TestClient, session_factory):
    # TODO: Replace arrange-setup with direct db-operation.

    # wrong card data:
    data = {
        "word_type": WordType.ADJECTIVE.value,  # wrong, needs to be corrected
        "relevance_id": "A",
        "relevance_description": "Beginner",
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
        "relevance_id": "A",
        "relevance_description": "Beginner",
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
        assert card.relevance.description == "Beginner"


def test_update_card_unhappy_path_returns_404_when_card_not_found(
    client: TestClient,
):
    # TODO: Replace arrange-setup with direct db-operation.

    # wrong card data:
    data = {
        "word_type": WordType.ADJECTIVE.value,  # wrong, needs to be corrected
        "relevance_id": "A",
        "relevance_description": "Beginner",
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
        "relevance_id": "A",
        "relevance_description": "Beginner",
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
    # TODO: Replace arrange-setup with direct db-operation.

    data = {
        "word_type": WordType.VERB.value,
        "relevance_id": "A",
        "relevance_description": "Beginner",
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
    # TODO: Replace arrange-setup with direct db-operation.
    
    data = {
        "word_type": WordType.VERB.value,
        "relevance_id": "A",
        "relevance_description": "Beginner",
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
