"""SQLAlchemy record for user persistence."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from template.adapters.models.base import Base


class UserRecord(Base):
    """Persist the state of a user aggregate."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
