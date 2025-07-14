"""Tests for conversations database operations."""

import json
import sqlite3
import tempfile
import time
import unittest
import unittest.mock
import uuid
from pathlib import Path

from quinn.db.conversations import Conversation, Conversations
from quinn.db.database import get_db_connection


class TestConversations(unittest.TestCase):
    """Test cases for Conversations database operations."""

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
        """Inject the test database connection."""
        self.db_patcher = unittest.mock.patch(
            "quinn.db.database.DATABASE_FILE", str(self.db_file)
        )
        self.db_patcher.start()

    def tearDown(self) -> None:
        """Clean up the database after each test."""
        with get_db_connection() as conn:
            conn.execute("DELETE FROM conversations")
            conn.execute("DELETE FROM users")
            conn.commit()
        self.db_patcher.stop()

    def test_conversation_model_creation(self) -> None:
        """Test Conversation model creation with defaults."""
        conversation = Conversation(
            id="test-conv-1",
            user_id="test-user-1"
        )
        
        assert conversation.id == "test-conv-1"
        assert conversation.user_id == "test-user-1"
        assert conversation.status == "active"
        assert conversation.total_cost == 0.0
        assert conversation.message_count == 0
        assert conversation.title is None
        assert conversation.metadata is None
        assert isinstance(conversation.created_at, int)
        assert isinstance(conversation.updated_at, int)

    def test_conversation_model_with_metadata(self) -> None:
        """Test Conversation model with metadata."""
        metadata = {"source": "api", "version": "1.0"}
        conversation = Conversation(
            id="test-conv-2",
            user_id="test-user-2",
            title="Test Conversation",
            status="archived",
            total_cost=1.50,
            message_count=5,
            metadata=metadata
        )
        
        assert conversation.title == "Test Conversation"
        assert conversation.status == "archived"
        assert conversation.total_cost == 1.50
        assert conversation.message_count == 5
        assert conversation.metadata == metadata

    def test_create_conversation(self) -> None:
        """Test creating a conversation in the database."""
        # First create a user (required by foreign key)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, created_at, updated_at, email_addresses) VALUES (?, ?, ?, ?)",
                ("test-user-1", int(time.time()), int(time.time()), '["test@example.com"]')
            )
            conn.commit()

        conversation = Conversation(
            id="test-conv-1",
            user_id="test-user-1",
            title="Test Conversation"
        )
        
        # Should not raise an exception
        Conversations.create(conversation)
        
        # Verify it was created
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations WHERE id = ?", ("test-conv-1",))
            count = cursor.fetchone()[0]
            assert count == 1

    def test_get_conversation_by_id(self) -> None:
        """Test retrieving a conversation by ID."""
        # Create user first
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, created_at, updated_at, email_addresses) VALUES (?, ?, ?, ?)",
                ("test-user-2", int(time.time()), int(time.time()), '["test@example.com"]')
            )
            conn.commit()

        original = Conversation(
            id="test-conv-2",
            user_id="test-user-2",
            title="Test Conversation",
            status="active",
            total_cost=2.50,
            message_count=3,
            metadata={"key": "value"}
        )
        
        Conversations.create(original)
        retrieved = Conversations.get_by_id("test-conv-2")
        
        assert retrieved is not None
        assert retrieved.id == original.id
        assert retrieved.user_id == original.user_id
        assert retrieved.title == original.title
        assert retrieved.status == original.status
        assert retrieved.total_cost == original.total_cost
        assert retrieved.message_count == original.message_count
        assert retrieved.metadata == original.metadata

    def test_get_conversation_by_id_not_found(self) -> None:
        """Test retrieving a non-existent conversation."""
        result = Conversations.get_by_id("non-existent")
        assert result is None

    def test_get_conversations_by_user(self) -> None:
        """Test retrieving all conversations for a user."""
        # Create user first
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, created_at, updated_at, email_addresses) VALUES (?, ?, ?, ?)",
                ("test-user-3", int(time.time()), int(time.time()), '["test@example.com"]')
            )
            conn.commit()

        conv1 = Conversation(id="conv-1", user_id="test-user-3", title="First")
        conv2 = Conversation(id="conv-2", user_id="test-user-3", title="Second")
        
        Conversations.create(conv1)
        Conversations.create(conv2)
        
        user_conversations = Conversations.get_by_user("test-user-3")
        
        assert len(user_conversations) == 2
        conversation_ids = {conv.id for conv in user_conversations}
        assert conversation_ids == {"conv-1", "conv-2"}

    def test_update_conversation(self) -> None:
        """Test updating an existing conversation."""
        # Create user first
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, created_at, updated_at, email_addresses) VALUES (?, ?, ?, ?)",
                ("test-user-4", int(time.time()), int(time.time()), '["test@example.com"]')
            )
            conn.commit()

        conversation = Conversation(
            id="test-conv-update",
            user_id="test-user-4",
            title="Original Title"
        )
        
        Conversations.create(conversation)
        
        # Update the conversation
        conversation.title = "Updated Title"
        conversation.status = "archived"
        conversation.total_cost = 5.0
        conversation.message_count = 10
        conversation.metadata = {"updated": True}
        
        original_updated_at = conversation.updated_at
        # Mock time to simulate timestamp change without actual delay
        with unittest.mock.patch('time.time', return_value=time.time() + 2):
            Conversations.update(conversation)
        
        # Verify the update
        retrieved = Conversations.get_by_id("test-conv-update")
        assert retrieved is not None
        assert retrieved.title == "Updated Title"
        assert retrieved.status == "archived"
        assert retrieved.total_cost == 5.0
        assert retrieved.message_count == 10
        assert retrieved.metadata == {"updated": True}
        assert retrieved.updated_at > original_updated_at

    def test_delete_conversation(self) -> None:
        """Test deleting a conversation."""
        # Create user first
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, created_at, updated_at, email_addresses) VALUES (?, ?, ?, ?)",
                ("test-user-5", int(time.time()), int(time.time()), '["test@example.com"]')
            )
            conn.commit()

        conversation = Conversation(
            id="test-conv-delete",
            user_id="test-user-5"
        )
        
        Conversations.create(conversation)
        
        # Verify it exists
        assert Conversations.get_by_id("test-conv-delete") is not None
        
        # Delete it
        Conversations.delete("test-conv-delete")
        
        # Verify it's gone
        assert Conversations.get_by_id("test-conv-delete") is None

    def test_conversation_with_null_metadata(self) -> None:
        """Test conversation with null metadata handling."""
        # Create user first
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, created_at, updated_at, email_addresses) VALUES (?, ?, ?, ?)",
                ("test-user-6", int(time.time()), int(time.time()), '["test@example.com"]')
            )
            conn.commit()

        conversation = Conversation(
            id="test-conv-null",
            user_id="test-user-6",
            metadata=None
        )
        
        Conversations.create(conversation)
        retrieved = Conversations.get_by_id("test-conv-null")
        
        assert retrieved is not None
        assert retrieved.metadata is None


if __name__ == "__main__":
    unittest.main()