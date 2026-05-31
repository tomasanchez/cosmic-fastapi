"""Internal command and event dispatcher."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from template.domain.messages import Command, Event, Message
from template.service_layer.unit_of_work import AbstractUnitOfWork

log = logging.getLogger(__name__)

UnitOfWorkFactory = Callable[[], AbstractUnitOfWork]
CommandHandler = Callable[[Any, AbstractUnitOfWork], Any]
EventHandler = Callable[[Any], None]


class UnsupportedMessageType(TypeError):
    """Raised when a message has neither command nor event semantics."""

    def __init__(self, message: Message):
        """Initialize the error for an unsupported message."""
        super().__init__(f"Unsupported message type: {type(message).__name__}")


class MessageBus:
    """Dispatch commands and events to configured handlers."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        command_handlers: dict[type, CommandHandler],
        event_handlers: dict[type, list[EventHandler]],
    ):
        """Initialize the message bus."""
        self.uow_factory = uow_factory
        self.command_handlers = command_handlers
        self.event_handlers = event_handlers

    def handle(self, message: Message) -> Any:
        """Dispatch one message and drain any resulting domain events."""
        queue = [message]
        result = None
        while queue:
            current = queue.pop(0)
            if isinstance(current, Command):
                result = self._handle_command(current, queue)
            elif isinstance(current, Event):
                self._handle_event(current)
            else:
                raise UnsupportedMessageType(current)
        return result

    def _handle_command(self, command: Command, queue: list[Message]) -> Any:
        """Dispatch a command and collect resulting events."""
        uow = self.uow_factory()
        handler = self.command_handlers[type(command)]
        result = handler(command, uow)
        queue.extend(uow.collect_new_events())
        return result

    def _handle_event(self, event: Event) -> None:
        """Dispatch an event to every interested handler."""
        for handler in self.event_handlers.get(type(event), []):
            try:
                handler(event)
            except Exception:
                log.exception("Exception handling event %s", event)
