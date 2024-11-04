from datetime import datetime, timezone

from pydantic import BaseModel, computed_field

from models.status import StatusEnum


class Event(BaseModel):
    id: str
    coefficient: float
    deadline_utc: datetime
    status: StatusEnum

    @computed_field
    @property
    def is_active(self) -> bool:
        return self.status == StatusEnum.pending and self.deadline_utc > datetime.now(
            timezone.utc
        )
