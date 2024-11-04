import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from dependencies import bets_repository, line_provider
from models.bet import Bet, BetOutcomeEnum, BetStatus, BetStatusEnum
from models.event import Event, EventStatusEnum
from repositories.bets import (BaseBetsRepository,
                               PlaceBetDuplicateEventIdException)
from services.line_provider import BaseLineProviderService

log = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["bets"])


@router.get("/events")
async def list_events(
    line_provider: Annotated[BaseLineProviderService, Depends(line_provider)]
) -> list[Event]:
    return await line_provider.fetch_active_events()


@router.get("/bets")
async def list_bets(
    bets_repository: Annotated[BaseBetsRepository, Depends(bets_repository)],
    line_provider: Annotated[BaseLineProviderService, Depends(line_provider)],
) -> list[BetStatus]:
    bet_statuses: list[BetStatus] = []
    all_bets = await bets_repository.get_bets()
    batch_size = 20
    for i in range(0, len(all_bets), batch_size):
        bets = all_bets[i : i + batch_size]
        event_ids = {bet.event_id for _, bet in bets}
        events = {
            event.id: event
            for event in await line_provider.fetch_events_by_ids(event_ids)
        }
        for bet_id, bet in bets:
            event = events.get(bet.event_id)
            status = BetStatusEnum.pending
            if event is not None and not event.status == EventStatusEnum.pending:
                both_fst_win = (
                    bet.outcome == BetOutcomeEnum.fst_win
                    and event.status == EventStatusEnum.fst_win
                )
                both_snd_win = (
                    bet.outcome == BetOutcomeEnum.snd_win
                    and event.status == EventStatusEnum.snd_win
                )
                if both_fst_win or both_snd_win:
                    status = BetStatusEnum.won
                else:
                    status = BetStatusEnum.lost
            bet_statuses.append(BetStatus(id=bet_id, status=status))
    return bet_statuses


@router.post("/bet")
async def place_bet(
    bet: Bet,
    bets_repository: Annotated[BaseBetsRepository, Depends(bets_repository)],
    line_provider: Annotated[BaseLineProviderService, Depends(line_provider)],
) -> int:
    events = await line_provider.fetch_events_by_ids(ids=[bet.event_id])
    if not events:
        raise HTTPException(status_code=400, detail="Event not found")
    event = events[0]
    if not event.is_active:
        raise HTTPException(status_code=400, detail="Can't bet on this event")
    try:
        bet_id = await bets_repository.place_bet(bet)
    except PlaceBetDuplicateEventIdException:
        raise HTTPException(status_code=409, detail="Bet already placed")
    return bet_id
