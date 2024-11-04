from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from routes.bets import router as bets_router
from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = create_async_engine(url=settings.postgres.url, echo=True)
    yield
    if app.state.engine:
        await app.state.engine.dispose()


app = FastAPI(title="Bet Maker", summary="", lifespan=lifespan)
app.include_router(bets_router)


@app.get("/healthcheck", include_in_schema=False)
def healthcheck() -> str:
    return ""
