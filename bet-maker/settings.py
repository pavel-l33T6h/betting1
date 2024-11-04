from pydantic import BaseModel
from pydantic_settings import BaseSettings


class LineProviderSettings(BaseModel):
    address: str = "line-provider:8100"


class PostgresSettings(BaseModel):
    url: str = "postgresql+psycopg://bets:1234@postgres:5432/bets"


class Settings(BaseSettings):
    line_provider: LineProviderSettings = LineProviderSettings()
    postgres: PostgresSettings = PostgresSettings()


settings = Settings()
