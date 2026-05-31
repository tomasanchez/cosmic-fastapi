"""Test suite for user application handlers."""

from uuid import UUID

import pytest

from template.domain.commands.user import RegisterUser
from template.domain.models.user import User
from template.service_layer.handlers import EmailAlreadyRegistered, register_user
from template.service_layer.unit_of_work import AbstractUnitOfWork


class FakeUserRepository:
    """Store user aggregates in memory for application tests."""

    def __init__(self, users: list[User] | None = None):
        """Initialize the fake repository."""
        self.users = users or []
        self.seen: list[User] = []

    def add(self, user: User) -> None:
        """Add a user."""
        self.users.append(user)
        self.seen.append(user)

    def get(self, user_id: UUID) -> User | None:
        """Return a user by identity."""
        user = next((user for user in self.users if user.id == user_id), None)
        if user:
            self.seen.append(user)
        return user

    def get_by_email(self, email: str) -> User | None:
        """Return a user by normalized email."""
        user = next((user for user in self.users if user.email == email.strip().lower()), None)
        if user:
            self.seen.append(user)
        return user


class FakeUnitOfWork(AbstractUnitOfWork):
    """Provide an in-memory transaction boundary."""

    def __init__(self, users: list[User] | None = None):
        """Initialize fake repositories."""
        self.users = FakeUserRepository(users)
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        """Record a commit."""
        self.committed = True

    def rollback(self) -> None:
        """Record a rollback."""
        self.rolled_back = True


class TestRegisterUser:
    """Test cases for registration orchestration."""

    def test_registers_user_and_commits(self):
        """
        GIVEN a registration command and an empty repository
        WHEN the registration handler executes
        THEN the user is stored and the transaction commits
        """
        # GIVEN
        command = RegisterUser(name="Ada Lovelace", email="ada@example.com")
        uow = FakeUnitOfWork()

        # WHEN
        user_id = register_user(command, uow)

        # THEN
        assert user_id == command.user_id
        assert uow.committed
        assert uow.users.get(command.user_id) is not None

    def test_rejects_an_existing_email(self):
        """
        GIVEN an existing user
        WHEN another registration uses the same normalized email
        THEN the registration handler rejects the command
        """
        # GIVEN
        existing_user = User.register(name="Ada Lovelace", email="ada@example.com")
        uow = FakeUnitOfWork([existing_user])

        # WHEN / THEN
        with pytest.raises(EmailAlreadyRegistered):
            register_user(RegisterUser(name="Other Ada", email=" ADA@example.com "), uow)
