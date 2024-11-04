from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_brokers: str = "kafka:9092"
    kafka_topic: str = "lines"


settings = Settings()
