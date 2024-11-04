from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from models.bet import Bet


class BetsRepositoryException(Exception):
    pass


class PlaceBetDuplicateEventIdException(BetsRepositoryException):
    pass


class BaseBetsRepository:
    async def place_bet(self, bet: Bet) -> int:
        raise NotImplementedError

    async def get_bets(self) -> list[tuple[int, Bet]]:
        raise NotImplementedError


class BetsRepository(BaseBetsRepository):
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def place_bet(self, bet: Bet) -> int:
        async with self._engine.connect() as conn:
            params = {
                "event_id": bet.event_id,
                "amount": bet.amount,
                "outcome": bet.outcome,
            }
            try:
                res = await conn.execute(
                    text(
                        "INSERT INTO bets (event_id, amount, outcome) VALUES (:event_id, :amount, :outcome) RETURNING id"
                    ),
                    params,
                )
                await conn.commit()
            except IntegrityError as err:
                raise PlaceBetDuplicateEventIdException() from err
            return res.scalar_one()

    async def get_bets(self) -> list[tuple[int, Bet]]:
        async with self._engine.connect() as conn:
            res = await conn.execute(
                text("SELECT id, event_id, amount, outcome FROM bets")
            )
            return [
                (r.id, Bet(event_id=r.event_id, amount=r.amount, outcome=r.outcome))
                for r in res.fetchall()
            ]
