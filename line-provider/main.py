import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request

from consumer import consume
from routes.events import router as events_router

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.ensure_future(consume(app))
    yield
    task.cancel()


app = FastAPI(title="Line Provider", summary="", lifespan=lifespan)
app.include_router(events_router)


@app.get("/healthcheck", include_in_schema=False)
def healthcheck(request: Request) -> str:
    if not request.app.state.events_ready:
        raise HTTPException(status_code=503, detail="Backfilling events in progress")
    return ""
