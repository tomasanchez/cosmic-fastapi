"""Test suite for internal message dispatch."""

from functools import partial
from unittest.mock import patch

import pytest

from template.domain.commands.user import RegisterUser
from template.domain.events.user import UserRegistered
from template.domain.messages import Message
from template.service_layer.handlers import publish_user_registered, register_user
from template.service_layer.messagebus import MessageBus
from tests.unit.service_layer.test_handlers import FakeUnitOfWork


class TestMessageBus:
    """Test cases for internal command and event dispatch."""

    def test_dispatches_events_raised_by_command_handlers(self):
        """
        GIVEN a message bus with registration and publication handlers
        WHEN a registration command is dispatched
        THEN the resulting domain event is published
        """
        # GIVEN
        published: list[UserRegistered] = []
        uow = FakeUnitOfWork()
        bus = MessageBus(
            uow_factory=lambda: uow,
            command_handlers={RegisterUser: register_user},
            event_handlers={UserRegistered: [partial(publish_user_registered, publish=published.append)]},
        )

        # WHEN
        command = RegisterUser(name="Ada Lovelace", email="ada@example.com")
        user_id = bus.handle(command)

        # THEN
        assert user_id == command.user_id
        assert published == [UserRegistered(user_id=command.user_id, email="ada@example.com")]

    def test_logs_event_handler_failures_and_continues(self):
        """
        GIVEN an event handler that raises an exception
        WHEN a domain event is dispatched
        THEN the failure is logged without failing the command
        """

        # GIVEN
        def fail_to_publish(event: UserRegistered) -> None:
            raise RuntimeError(event.email)

        bus = MessageBus(
            uow_factory=FakeUnitOfWork,
            command_handlers={RegisterUser: register_user},
            event_handlers={UserRegistered: [fail_to_publish]},
        )

        # WHEN
        with patch("template.service_layer.messagebus.log.exception") as log_exception:
            user_id = bus.handle(RegisterUser(name="Ada Lovelace", email="ada@example.com"))

        # THEN
        assert user_id is not None
        log_exception.assert_called_once()

    def test_rejects_messages_without_command_or_event_semantics(self):
        """
        GIVEN a base message without command or event semantics
        WHEN the message bus receives it
        THEN the unsupported message is rejected
        """
        # GIVEN
        bus = MessageBus(uow_factory=FakeUnitOfWork, command_handlers={}, event_handlers={})

        # WHEN / THEN
        with pytest.raises(TypeError, match="Unsupported message type"):
            bus.handle(Message())
