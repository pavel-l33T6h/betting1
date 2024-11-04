from enum import Enum


class StatusEnum(str, Enum):
    pending = "pending"
    fst_win = "fst_win"
    snd_win = "snd_win"
