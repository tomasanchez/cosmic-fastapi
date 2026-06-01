"""Kafka relay settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    """Configure the optional Kafka outbox relay."""

    BOOTSTRAP_SERVERS: str = "localhost:9092"
    USER_EVENTS_TOPIC: str = "users.events"
    PUBLISH_TIMEOUT: float = 10.0
    RELAY_INTERVAL: float = 1.0
    BATCH_SIZE: int = 100

    model_config = SettingsConfigDict(case_sensitive=True, env_prefix="KAFKA_")
