"""SQLAlchemy record for transactional outbox persistence."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from template.adapters.models.base import Base


class OutboxRecord(Base):
    """Persist an integration event until a relay publishes it."""

    __tablename__ = "outbox_events"

    id: Mapped[str] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    aggregate_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
