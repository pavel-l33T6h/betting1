import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from models.event import Event

log = logging.getLogger(f"uvicorn.{__name__}")

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/")
def list_events(
    request: Request, ids: Annotated[list[str], Query(alias="id")] = None
) -> list[Event]:
    if ids is None:
        return []
    max_ids_n = 20
    if len(ids) > max_ids_n:
        raise HTTPException(status_code=400, detail=f"At most {max_ids_n} ids allowed")
    return [
        request.app.state.events[event_id]
        for event_id in ids
        if event_id in request.app.state.events
    ]


@router.get("/all_active")
def list_active_events(request: Request) -> list[Event]:
    return [v for _, v in request.app.state.events.items() if v.is_active]


@router.get("/{event_id}")
def get_event(event_id: str, request: Request) -> Event:
    event = request.app.state.events.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
