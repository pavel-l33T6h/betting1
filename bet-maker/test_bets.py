import pytest
from fastapi.testclient import TestClient

from dependencies import bets_repository, line_provider
from main import app
from models.bet import Bet
from models.event import Event, EventStatusEnum
from repositories.bets import (BaseBetsRepository,
                               PlaceBetDuplicateEventIdException)
from services.line_provider import BaseLineProviderService


class MockBetsRepository(BaseBetsRepository):
    def __init__(self):
        self.counter = 0
        self.bets = []

    async def place_bet(self, bet: Bet) -> int:
        if bet.event_id in {b.event_id for _, b in self.bets}:
            raise PlaceBetDuplicateEventIdException()
        self.counter += 1
        self.bets.append((self.counter, bet))
        return self.counter

    async def get_bets(self) -> list[tuple[int, Bet]]:
        return self.bets


class MockLineProviderService(BaseLineProviderService):
    def __init__(self):
        self.events = [
            Event(
                id="e1",
                coefficient=0.95,
                status=EventStatusEnum.pending,
                is_active=True,
            ),
            Event(
                id="e2",
                coefficient=0.95,
                status=EventStatusEnum.pending,
                is_active=False,
            ),
        ]

    async def fetch_active_events(self) -> list[Event]:
        return [event for event in self.events if event.is_active]

    async def fetch_events_by_ids(self, ids: set[str]) -> list[Event]:
        return [event for event in self.events if event.id in ids]


client = TestClient(app)


@pytest.fixture
def install_overrides():
    repo = MockBetsRepository()
    app.dependency_overrides[bets_repository] = lambda: repo
    service = MockLineProviderService()
    app.dependency_overrides[line_provider] = lambda: service
    yield repo, service
    app.dependency_overrides = {}


def test_events(install_overrides):
    response = client.get("/events")
    assert response.status_code == 200
    assert [e["id"] for e in response.json()] == ["e1"]


def test_place_bet_repeat(install_overrides):
    response = client.get("/bets")
    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/bet", json={"event_id": "e1", "amount": 100.0, "outcome": "fst_win"}
    )
    assert response.status_code == 200
    assert response.json() == 1

    response = client.post(
        "/bet", json={"event_id": "e1", "amount": 100.0, "outcome": "fst_win"}
    )
    assert response.status_code == 409


def test_place_bet_inactive(install_overrides):
    response = client.get("/bets")
    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/bet", json={"event_id": "e2", "amount": 100.0, "outcome": "fst_win"}
    )
    assert response.status_code == 400


def test_place_bet_not_found(install_overrides):
    response = client.get("/bets")
    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/bet", json={"event_id": "e3", "amount": 100.0, "outcome": "fst_win"}
    )
    assert response.status_code == 400


def test_place_bet_negative_amount(install_overrides):
    response = client.get("/bets")
    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/bet", json={"event_id": "e1", "amount": -100.0, "outcome": "fst_win"}
    )
    assert response.status_code == 422


def test_place_bet(install_overrides):
    response = client.get("/bets")
    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/bet", json={"event_id": "e1", "amount": 100.0, "outcome": "fst_win"}
    )
    assert response.status_code == 200
    assert response.json() == 1

    response = client.get("/bets")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "status": "pending"}]

    _, line_provider = install_overrides

    line_provider.events = [
        Event(
            id="e1", coefficient=0.95, status=EventStatusEnum.fst_win, is_active=False
        )
    ]

    response = client.get("/bets")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "status": "won"}]

    line_provider.events = [
        Event(
            id="e1", coefficient=0.95, status=EventStatusEnum.snd_win, is_active=False
        )
    ]

    response = client.get("/bets")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "status": "lost"}]
