"""Integration tests for Alembic migrations."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


class TestMigrations:
    """Test cases for relational schema migrations."""

    def test_upgrades_a_blank_database_to_head(self, tmp_path: Path):
        """
        GIVEN a blank SQLite database
        WHEN Alembic upgrades the database to head
        THEN the user schema and Alembic revision table exist
        """
        # GIVEN
        database_path = tmp_path / "migration-test.db"
        database_url = f"sqlite+pysqlite:///{database_path.as_posix()}"
        config = Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", database_url)

        # WHEN
        command.upgrade(config, "head")

        # THEN
        tables = inspect(create_engine(database_url)).get_table_names()
        assert "alembic_version" in tables
        assert "users" in tables
