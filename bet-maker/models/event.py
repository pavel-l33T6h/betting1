from enum import Enum

from pydantic import BaseModel


class EventStatusEnum(str, Enum):
    pending = "pending"
    fst_win = "fst_win"
    snd_win = "snd_win"


class Event(BaseModel):
    id: str
    coefficient: float
    status: EventStatusEnum
    is_active: bool
