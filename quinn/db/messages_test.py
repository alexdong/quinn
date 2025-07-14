"""Tests for messages database operations."""

import json
import sqlite3
import tempfile
import time
import unittest
import unittest.mock
import uuid
from pathlib import Path

from quinn.db.database import get_db_connection
from quinn.db.messages import Message, Messages


class TestMessages(unittest.TestCase):
    """Test cases for Messages database operations."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a test database and create tables."""
        cls.db_file = Path(tempfile.mktemp(suffix=".db"))
        with (
            sqlite3.connect(cls.db_file) as conn,
            Path("quinn/db/schema.sql").open() as f,
        ):
            conn.executescript(f.read())

    @classmethod
    def tearDownClass(cls) -> None:
        """Remove the test database."""
        if cls.db_file.exists():
            cls.db_file.unlink()

    def setUp(self) -> None:
        """Inject the test database connection and create test data."""
        self.db_patcher = unittest.mock.patch(
            "quinn.db.database.DATABASE_FILE", str(self.db_file)
        )
        self.db_patcher.start()
        
        # Create test user and conversation for foreign key constraints
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (id, created_at, updated_at, email_addresses) VALUES (?, ?, ?, ?)",
                ("test-user-1", int(time.time()), int(time.time()), '["test@example.com"]')
            )
            cursor.execute(
                "INSERT OR IGNORE INTO conversations (id, user_id, created_at, updated_at) VALUES (?, ?, ?, ?)",
                ("test-conv-1", "test-user-1", int(time.time()), int(time.time()))
            )
            conn.commit()

    def tearDown(self) -> None:
        """Clean up the database after each test."""
        with get_db_connection() as conn:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM conversations")
            conn.execute("DELETE FROM users")
            conn.commit()
        self.db_patcher.stop()

    def test_message_model_creation(self) -> None:
        """Test Message model creation with defaults."""
        message = Message(
            id="test-msg-1",
            conversation_id="test-conv-1",
            user_id="test-user-1"
        )
        
        assert message.id == "test-msg-1"
        assert message.conversation_id == "test-conv-1"
        assert message.user_id == "test-user-1"
        assert message.system_prompt == ""
        assert message.user_content == ""
        assert message.assistant_content == ""
        assert message.metadata is None
        assert isinstance(message.created_at, int)
        assert isinstance(message.last_updated_at, int)

    def test_message_model_with_content(self) -> None:
        """Test Message model with content."""
        metadata = {"tokens": 100, "model": "gpt-4"}
        message = Message(
            id="test-msg-2",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            system_prompt="You are a helpful assistant",
            user_content="Hello, how are you?",
            assistant_content="I'm doing well, thank you!",
            metadata=metadata
        )
        
        assert message.system_prompt == "You are a helpful assistant"
        assert message.user_content == "Hello, how are you?"
        assert message.assistant_content == "I'm doing well, thank you!"
        assert message.metadata == metadata

    def test_create_message(self) -> None:
        """Test creating a message in the database."""
        message = Message(
            id="test-msg-create",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            user_content="Test message"
        )
        
        # Should not raise an exception
        Messages.create(message)
        
        # Verify it was created
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM messages WHERE id = ?", ("test-msg-create",))
            count = cursor.fetchone()[0]
            assert count == 1

    def test_get_message_by_id(self) -> None:
        """Test retrieving a message by ID."""
        original = Message(
            id="test-msg-get",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            system_prompt="System prompt",
            user_content="User content",
            assistant_content="Assistant content",
            metadata={"key": "value"}
        )
        
        Messages.create(original)
        retrieved = Messages.get_by_id("test-msg-get")
        
        assert retrieved is not None
        assert retrieved.id == original.id
        assert retrieved.conversation_id == original.conversation_id
        assert retrieved.user_id == original.user_id
        assert retrieved.system_prompt == original.system_prompt
        assert retrieved.user_content == original.user_content
        assert retrieved.assistant_content == original.assistant_content
        assert retrieved.metadata == original.metadata

    def test_get_message_by_id_not_found(self) -> None:
        """Test retrieving a non-existent message."""
        result = Messages.get_by_id("non-existent")
        assert result is None

    def test_get_messages_by_conversation(self) -> None:
        """Test retrieving all messages for a conversation."""
        msg1 = Message(
            id="msg-1",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            user_content="First message"
        )
        msg2 = Message(
            id="msg-2",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            assistant_content="Second message"
        )
        
        Messages.create(msg1)
        time.sleep(0.001)  # Ensure different timestamps
        Messages.create(msg2)
        
        conversation_messages = Messages.get_by_conversation("test-conv-1")
        
        assert len(conversation_messages) == 2
        # Should be ordered by created_at ASC
        assert conversation_messages[0].id == "msg-1"
        assert conversation_messages[1].id == "msg-2"

    def test_update_message(self) -> None:
        """Test updating an existing message."""
        message = Message(
            id="test-msg-update",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            user_content="Original content"
        )
        
        Messages.create(message)
        
        # Update the message
        message.system_prompt = "Updated system prompt"
        message.user_content = "Updated user content"
        message.assistant_content = "Updated assistant content"
        message.metadata = {"updated": True}
        
        original_updated_at = message.last_updated_at
        # Mock time to simulate timestamp change without actual delay
        with unittest.mock.patch('time.time', return_value=time.time() + 2):
            Messages.update(message)
        
        # Verify the update
        retrieved = Messages.get_by_id("test-msg-update")
        assert retrieved is not None
        assert retrieved.system_prompt == "Updated system prompt"
        assert retrieved.user_content == "Updated user content"
        assert retrieved.assistant_content == "Updated assistant content"
        assert retrieved.metadata == {"updated": True}
        assert retrieved.last_updated_at > original_updated_at

    def test_delete_message(self) -> None:
        """Test deleting a message."""
        message = Message(
            id="test-msg-delete",
            conversation_id="test-conv-1",
            user_id="test-user-1"
        )
        
        Messages.create(message)
        
        # Verify it exists
        assert Messages.get_by_id("test-msg-delete") is not None
        
        # Delete it
        Messages.delete("test-msg-delete")
        
        # Verify it's gone
        assert Messages.get_by_id("test-msg-delete") is None

    def test_message_with_null_metadata(self) -> None:
        """Test message with null metadata handling."""
        message = Message(
            id="test-msg-null",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            metadata=None
        )
        
        Messages.create(message)
        retrieved = Messages.get_by_id("test-msg-null")
        
        assert retrieved is not None
        assert retrieved.metadata is None

    def test_message_ordering_by_created_at(self) -> None:
        """Test that messages are returned in created_at order."""
        # Create messages with explicit timestamps
        base_time = int(time.time())
        
        msg1 = Message(
            id="msg-order-1",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            created_at=base_time,
            user_content="First"
        )
        msg2 = Message(
            id="msg-order-2",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            created_at=base_time + 1,
            user_content="Second"
        )
        msg3 = Message(
            id="msg-order-3",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            created_at=base_time + 2,
            user_content="Third"
        )
        
        # Create in reverse order
        Messages.create(msg3)
        Messages.create(msg1)
        Messages.create(msg2)
        
        # Should be returned in chronological order
        messages = Messages.get_by_conversation("test-conv-1")
        assert len(messages) == 3
        assert messages[0].user_content == "First"
        assert messages[1].user_content == "Second"
        assert messages[2].user_content == "Third"

    def test_message_json_metadata_serialization(self) -> None:
        """Test that metadata is properly serialized/deserialized as JSON."""
        complex_metadata = {
            "tokens": 150,
            "model": "gpt-4",
            "nested": {"key": "value", "number": 42},
            "list": [1, 2, 3]
        }
        
        message = Message(
            id="test-msg-json",
            conversation_id="test-conv-1",
            user_id="test-user-1",
            metadata=complex_metadata
        )
        
        Messages.create(message)
        retrieved = Messages.get_by_id("test-msg-json")
        
        assert retrieved is not None
        assert retrieved.metadata == complex_metadata


if __name__ == "__main__":
    unittest.main()