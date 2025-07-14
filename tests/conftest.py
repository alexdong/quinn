"""Shared pytest fixtures for all tests in the tests/ directory."""

import sqlite3
import tempfile
import time
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from quinn.db.conversations import Conversation, Conversations
from quinn.db.database import get_db_connection
from quinn.db.messages import Message, Messages
from quinn.db.users import User, Users


@pytest.fixture(scope="session")
def test_db_schema():
    """Load the database schema for testing."""
    schema_path = Path("quinn/db/schema.sql")
    if not schema_path.exists():
        pytest.skip(f"Database schema not found at {schema_path}")
    return schema_path.read_text()


@pytest.fixture
def temp_test_db(test_db_schema):
    """Create a temporary database file for testing with full schema."""
    db_file = Path(tempfile.mktemp(suffix=".db"))
    
    # Create tables in test database
    with sqlite3.connect(db_file) as conn:
        conn.executescript(test_db_schema)
    
    # Patch DATABASE_FILE to use test database
    with patch("quinn.db.database.DATABASE_FILE", str(db_file)):
        yield db_file
    
    # Cleanup
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def clean_test_db(temp_test_db):
    """Provide a clean database that gets cleared after each test."""
    yield temp_test_db
    
    # Clean up all tables after each test
    with patch("quinn.db.database.DATABASE_FILE", str(temp_test_db)):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM conversations") 
            conn.execute("DELETE FROM users")
            conn.commit()


@pytest.fixture
def sample_user():
    """Provide a sample user for testing."""
    return User(
        id=str(uuid.uuid4()),
        email_addresses=["test@example.com", "test2@example.com"],
        name="Test User",
        settings={"theme": "dark", "notifications": True}
    )


@pytest.fixture
def sample_conversation(sample_user):
    """Provide a sample conversation for testing."""
    return Conversation(
        id=str(uuid.uuid4()),
        user_id=sample_user.id,
        title="Test Conversation",
        status="active",
        total_cost=0.05,
        message_count=2,
        metadata={"topic": "testing", "priority": "high"}
    )


@pytest.fixture
def sample_message(sample_user, sample_conversation):
    """Provide a sample message for testing."""
    return Message(
        id=str(uuid.uuid4()),
        conversation_id=sample_conversation.id,
        user_id=sample_user.id,
        system_prompt="You are a helpful assistant",
        user_content="Hello, how are you?",
        assistant_content="I'm doing well, thank you!",
        metadata={
            "tokens_used": 25,
            "cost_usd": 0.001,
            "response_time_ms": 500,
            "model_used": "gpt-4",
            "prompt_version": "v240715-120000"
        }
    )


@pytest.fixture
def db_with_sample_data(clean_test_db, sample_user, sample_conversation, sample_message):
    """Set up database with sample user, conversation, and message data."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_test_db)):
        # Create user first (required for foreign keys)
        Users.create(sample_user)
        
        # Create conversation (requires user)
        Conversations.create(sample_conversation)
        
        # Create message (requires user and conversation)
        Messages.create(sample_message)
        
        yield {
            "db_file": clean_test_db,
            "user": sample_user,
            "conversation": sample_conversation,
            "message": sample_message
        }


@pytest.fixture
def multiple_users():
    """Provide multiple users for testing user-related operations."""
    return [
        User(
            id=str(uuid.uuid4()),
            email_addresses=[f"user{i}@example.com"],
            name=f"Test User {i}",
            settings={"user_id": i, "theme": "light" if i % 2 == 0 else "dark"}
        )
        for i in range(1, 4)
    ]


@pytest.fixture
def multiple_conversations(sample_user):
    """Provide multiple conversations for testing conversation operations."""
    return [
        Conversation(
            id=str(uuid.uuid4()),
            user_id=sample_user.id,
            title=f"Conversation {i}",
            status="active" if i % 2 == 0 else "archived",
            total_cost=0.01 * i,
            message_count=i,
            metadata={"conversation_number": i}
        )
        for i in range(1, 4)
    ]


@pytest.fixture
def multiple_messages(sample_user, sample_conversation):
    """Provide multiple messages for testing message operations."""
    messages = []
    base_time = int(time.time())
    
    for i in range(1, 4):
        messages.append(Message(
            id=str(uuid.uuid4()),
            conversation_id=sample_conversation.id,
            user_id=sample_user.id,
            created_at=base_time + i * 10,  # Ensure chronological order
            user_content=f"User message {i}" if i % 2 == 1 else "",
            assistant_content=f"Assistant response {i}" if i % 2 == 0 else "",
            metadata={
                "message_number": i,
                "tokens_used": 10 * i,
                "cost_usd": 0.001 * i
            }
        ))
    
    return messages


@pytest.fixture
def db_with_multiple_data(clean_test_db, multiple_users, multiple_conversations, multiple_messages):
    """Set up database with multiple users, conversations, and messages."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_test_db)):
        # Create all users
        for user in multiple_users:
            Users.create(user)
        
        # Create conversations for first user
        for conversation in multiple_conversations:
            Conversations.create(conversation)
        
        # Create messages for first conversation
        for message in multiple_messages:
            Messages.create(message)
        
        yield {
            "db_file": clean_test_db,
            "users": multiple_users,
            "conversations": multiple_conversations,
            "messages": multiple_messages
        }


@pytest.fixture
def mock_time():
    """Provide a mock time function for testing time-dependent operations."""
    class MockTime:
        def __init__(self):
            self.current_time = 1640995200  # 2022-01-01 00:00:00 UTC
        
        def time(self):
            return self.current_time
        
        def advance(self, seconds):
            self.current_time += seconds
            return self.current_time
    
    return MockTime()


@pytest.fixture
def assert_db_state():
    """Provide helper functions for asserting database state."""
    class DbAssertions:
        @staticmethod
        def user_exists(user_id: str, db_file: Path) -> bool:
            """Check if user exists in database."""
            with patch("quinn.db.database.DATABASE_FILE", str(db_file)):
                return Users.get_by_id(user_id) is not None
        
        @staticmethod
        def conversation_exists(conversation_id: str, db_file: Path) -> bool:
            """Check if conversation exists in database."""
            with patch("quinn.db.database.DATABASE_FILE", str(db_file)):
                return Conversations.get_by_id(conversation_id) is not None
        
        @staticmethod
        def message_exists(message_id: str, db_file: Path) -> bool:
            """Check if message exists in database."""
            with patch("quinn.db.database.DATABASE_FILE", str(db_file)):
                return Messages.get_by_id(message_id) is not None
        
        @staticmethod
        def count_users(db_file: Path) -> int:
            """Count total users in database."""
            with patch("quinn.db.database.DATABASE_FILE", str(db_file)):
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM users")
                    return cursor.fetchone()[0]
        
        @staticmethod
        def count_conversations(db_file: Path) -> int:
            """Count total conversations in database."""
            with patch("quinn.db.database.DATABASE_FILE", str(db_file)):
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM conversations")
                    return cursor.fetchone()[0]
        
        @staticmethod
        def count_messages(db_file: Path) -> int:
            """Count total messages in database."""
            with patch("quinn.db.database.DATABASE_FILE", str(db_file)):
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM messages")
                    return cursor.fetchone()[0]
    
    return DbAssertions()