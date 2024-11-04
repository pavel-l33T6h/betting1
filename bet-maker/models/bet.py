from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class BetOutcomeEnum(str, Enum):
    fst_win = "fst_win"
    snd_win = "snd_win"


class Bet(BaseModel):
    event_id: str
    amount: Decimal = Field(decimal_places=2, gt=0.0)
    outcome: BetOutcomeEnum


class BetStatusEnum(str, Enum):
    pending = "pending"
    won = "won"
    lost = "lost"


class BetStatus(BaseModel):
    id: int
    status: BetStatusEnum
