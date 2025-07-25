"""Shared pytest fixtures for database tests."""

import sqlite3
import tempfile
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from quinn.db.database import get_db_connection


@pytest.fixture
def temp_db() -> Generator[Path]:
    """Create a temporary database file for testing."""
    db_file = Path(tempfile.mktemp(suffix=".db"))

    # Create tables in test database
    try:
        conn = sqlite3.connect(db_file)
        try:
            with Path("quinn/db/schema.sql").open() as f:
                conn.executescript(f.read())
            conn.commit()
        finally:
            conn.close()
    except Exception:
        # Clean up the file if database setup fails
        if db_file.exists():
            db_file.unlink()
        raise

    # Patch DATABASE_FILE to use test database
    with patch("quinn.db.database.DATABASE_FILE", str(db_file)):
        yield db_file

    # Cleanup
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def clean_db(temp_db: Path) -> Generator[Path]:
    """Provide a clean database that gets cleared after each test."""
    yield temp_db

    # Clean up all tables after each test
    with (
        patch("quinn.db.database.DATABASE_FILE", str(temp_db)),
        get_db_connection() as conn,
    ):
        conn.execute("DELETE FROM emails")
        conn.execute("DELETE FROM messages")
        conn.execute("DELETE FROM conversations")
        conn.execute("DELETE FROM users")
        conn.commit()


@pytest.fixture
def test_user_data() -> dict[str, Any]:
    """Provide test user data."""
    return {
        "id": "test-user-1",
        "email_addresses": ["test@example.com"],
        "name": "Test User",
        "settings": {"theme": "dark", "notifications": True},
    }


@pytest.fixture
def test_conversation_data() -> dict[str, Any]:
    """Provide test conversation data."""
    return {
        "id": "test-conv-1",
        "user_id": "test-user-1",
        "title": "Test Conversation",
        "status": "active",
        "total_cost": 0.05,
        "message_count": 2,
        "metadata": {"topic": "testing", "priority": "high"},
    }


@pytest.fixture
def test_message_data() -> dict[str, Any]:
    """Provide test message data."""
    return {
        "id": "test-msg-1",
        "conversation_id": "test-conv-1",
        "user_id": "test-user-1",
        "system_prompt": "You are a helpful assistant",
        "user_content": "Hello, how are you?",
        "assistant_content": "I'm doing well, thank you!",
        "metadata": {
            "tokens_used": 25,
            "cost_usd": 0.001,
            "response_time_ms": 500,
            "model_used": "gpt-4",
            "prompt_version": "v240715-120000",
        },
    }


@pytest.fixture
def setup_test_data(
    clean_db: Path,
    test_user_data: dict[str, Any],
    test_conversation_data: dict[str, Any],
    test_message_data: dict[str, Any],
) -> dict[str, Any]:
    """Set up test user and conversation for foreign key constraints."""
    with (
        patch("quinn.db.database.DATABASE_FILE", str(clean_db)),
        get_db_connection() as conn,
    ):
        cursor = conn.cursor()

        # Insert test user
        cursor.execute(
            "INSERT INTO users (id, created_at, updated_at, name, email_addresses, settings) VALUES (?, ?, ?, ?, ?, ?)",
            (
                test_user_data["id"],
                int(time.time()),
                int(time.time()),
                test_user_data["name"],
                '["test@example.com"]',
                '{"theme": "dark", "notifications": true}',
            ),
        )

        # Insert test conversation
        cursor.execute(
            "INSERT INTO conversations (id, user_id, created_at, updated_at, title, status, total_cost, message_count, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                test_conversation_data["id"],
                test_conversation_data["user_id"],
                int(time.time()),
                int(time.time()),
                test_conversation_data["title"],
                test_conversation_data["status"],
                test_conversation_data["total_cost"],
                test_conversation_data["message_count"],
                '{"topic": "testing", "priority": "high"}',
            ),
        )

        conn.commit()

    return {
        "test_user_data": test_user_data,
        "test_conversation_data": test_conversation_data,
        "test_message_data": test_message_data,
        "db_file": clean_db,
    }
