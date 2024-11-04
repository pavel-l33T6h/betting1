import logging

from fastapi import Request

from repositories.bets import BetsRepository
from services.line_provider import LineProviderService
from settings import settings

log = logging.getLogger(__name__)


def bets_repository(request: Request):
    return BetsRepository(request.app.state.engine)


async def line_provider():
    return LineProviderService(settings.line_provider.address)
