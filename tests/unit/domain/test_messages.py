"""Test suite for Pydantic application messages."""

from typing import Any, cast
from uuid import UUID

import pytest
from pydantic import ValidationError

from template.domain.commands.user import RegisterUser
from template.domain.events.user import UserRegistered


class TestMessages:
    """Test cases for immutable command and event schemas."""

    def test_serializes_commands_and_events(self):
        """
        GIVEN a Pydantic command and event
        WHEN the messages are serialized
        THEN adapters receive stable dictionary representations
        """
        # GIVEN
        command = RegisterUser(name="Ada Lovelace", email="ada@example.com")
        event = UserRegistered(user_id=command.user_id, email=command.email)

        # WHEN / THEN
        assert UUID(command.model_dump(mode="json")["userId"]) == command.user_id
        assert event.model_dump(mode="json") == {"userId": str(command.user_id), "email": "ada@example.com"}

    def test_parses_camel_case_commands(self):
        """
        GIVEN a camel-case JSON payload from an external adapter
        WHEN the command schema validates it
        THEN application code receives the typed command
        """
        # GIVEN
        user_id = "00000000-0000-0000-0000-000000000001"

        # WHEN
        command = RegisterUser.model_validate(
            {
                "name": "Ada Lovelace",
                "email": "ada@example.com",
                "settings": {"marketingEnabled": True, "backupEmail": "backup@example.com"},
                "userId": user_id,
            }
        )

        # THEN
        assert str(command.user_id) == user_id
        assert command.model_dump(mode="json")["settings"] == {
            "theme": "light",
            "language": "en",
            "marketingEnabled": True,
            "backupEmail": "backup@example.com",
        }

    @pytest.mark.parametrize(
        ("name", "email"),
        [
            ("", "ada@example.com"),
            ("Ada Lovelace", "not-an-email"),
        ],
    )
    def test_rejects_invalid_commands(self, name: str, email: str):
        """
        GIVEN invalid registration data from an external adapter
        WHEN the command schema validates it
        THEN Pydantic rejects the command before dispatch
        """
        # WHEN / THEN
        with pytest.raises(ValidationError):
            RegisterUser(name=name, email=email)

    def test_rejects_message_mutation(self):
        """
        GIVEN a frozen Pydantic command
        WHEN application code attempts to mutate it
        THEN Pydantic rejects the mutation
        """
        # GIVEN
        command = RegisterUser(name="Ada Lovelace", email="ada@example.com")

        # WHEN / THEN
        with pytest.raises(ValidationError):
            cast(Any, command).email = "other@example.com"
