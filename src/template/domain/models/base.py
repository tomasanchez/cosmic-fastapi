"""Shared domain model building blocks."""

from enum import Enum


class BaseEnum(str, Enum):
    """Base class for string enumerations used in the domain."""

    @classmethod
    def list(cls) -> list[str]:
        """Return all enumeration values."""
        return [member.value for member in cls]
