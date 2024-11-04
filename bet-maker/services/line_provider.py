import aiohttp

from models.event import Event


class BaseLineProviderService:
    async def fetch_active_events(self) -> list[Event]:
        raise NotImplementedError

    async def fetch_events_by_ids(self, ids: set[str]) -> list[Event]:
        raise NotImplementedError


class LineProviderService(BaseLineProviderService):
    def __init__(self, address: str):
        self._address = address

    async def fetch_active_events(self) -> list[Event]:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=2), raise_for_status=True
        ) as session:
            async with session.get(
                f"http://{self._address}/events/all_active"
            ) as response:
                events = await response.json()
                return [Event.model_validate(event) for event in events]

    async def fetch_events_by_ids(self, ids: set[str]) -> list[Event]:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=2), raise_for_status=True
        ) as session:
            async with session.get(
                f"http://{self._address}/events/", params={"id": list(ids)}
            ) as response:
                events = await response.json()
                return [Event.model_validate(event) for event in events]
