"""Shared SQLAlchemy persistence model helpers."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Provide the declarative base for persistence records."""
