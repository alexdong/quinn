import sqlite3
import unittest
import unittest.mock
import uuid
from pathlib import Path

from quinn.db.conversations import Conversation, Conversations
from quinn.db.database import get_db_connection
from quinn.db.messages import Message, Messages
from quinn.db.users import User, Users


class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Set up a test database and create tables."""
        cls.db_file = Path("test.db")
        with (
            sqlite3.connect(cls.db_file) as conn,
            Path("quinn/db/schema.sql").open() as f,
        ):
            conn.executescript(f.read())

    @classmethod
    def tearDownClass(cls) -> None:
        """Remove the test database."""
        cls.db_file.unlink()

    def setUp(self) -> None:
        """Inject the test database connection."""
        self.db_patcher = unittest.mock.patch(
            "quinn.db.database.DATABASE_FILE", self.db_file
        )
        self.db_patcher.start()

    def tearDown(self) -> None:
        """Clean up the database after each test."""
        with get_db_connection() as conn:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM conversations")
            conn.execute("DELETE FROM users")
            conn.commit()
        self.db_patcher.stop()

    def test_create_and_get_user(self) -> None:
        """Test creating and retrieving a user."""
        user = User(id=str(uuid.uuid4()), email_addresses=["test@example.com"])
        Users.create(user)
        retrieved_user = Users.get_by_id(user.id)
        assert user == retrieved_user

    def test_create_and_get_conversation(self) -> None:
        """Test creating and retrieving a conversation."""
        user = User(id=str(uuid.uuid4()), email_addresses=["test@example.com"])
        Users.create(user)
        conversation = Conversation(id=str(uuid.uuid4()), user_id=user.id)
        Conversations.create(conversation)
        retrieved_conversation = Conversations.get_by_id(conversation.id)
        assert conversation == retrieved_conversation

    def test_create_and_get_message(self) -> None:
        """Test creating and retrieving a message."""
        user = User(id=str(uuid.uuid4()), email_addresses=["test@example.com"])
        Users.create(user)
        conversation = Conversation(id=str(uuid.uuid4()), user_id=user.id)
        Conversations.create(conversation)
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            user_id=user.id,
            user_content="Hello",
        )
        Messages.create(message)
        retrieved_message = Messages.get_by_id(message.id)
        assert message == retrieved_message

    def test_get_conversations_by_user(self) -> None:
        """Test retrieving conversations by user."""
        user = User(id=str(uuid.uuid4()), email_addresses=["test@example.com"])
        Users.create(user)
        conv1 = Conversation(id=str(uuid.uuid4()), user_id=user.id)
        conv2 = Conversation(id=str(uuid.uuid4()), user_id=user.id)
        Conversations.create(conv1)
        Conversations.create(conv2)
        user_conversations = Conversations.get_by_user(user.id)
        expected_conversation_count = 2
        assert len(user_conversations) == expected_conversation_count

    def test_get_messages_by_conversation(self) -> None:
        """Test retrieving messages by conversation."""
        user = User(id=str(uuid.uuid4()), email_addresses=["test@example.com"])
        Users.create(user)
        conversation = Conversation(id=str(uuid.uuid4()), user_id=user.id)
        Conversations.create(conversation)
        msg1 = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            user_id=user.id,
            user_content="Hello",
        )
        msg2 = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            user_id=user.id,
            assistant_content="Hi there!",
        )
        Messages.create(msg1)
        Messages.create(msg2)
        conversation_messages = Messages.get_by_conversation(conversation.id)
        expected_message_count = 2
        assert len(conversation_messages) == expected_message_count


if __name__ == "__main__":
    unittest.main()
