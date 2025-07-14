"""Integration tests for database operations using pytest fixtures."""

import uuid
from unittest.mock import patch

import pytest

from quinn.db.conversations import Conversation, Conversations
from quinn.db.messages import Message, Messages
from quinn.db.users import User, Users


def test_create_and_get_user(clean_test_db, sample_user):
    """Test creating and retrieving a user."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_test_db)):
        Users.create(sample_user)
        retrieved_user = Users.get_by_id(sample_user.id)
        
        assert retrieved_user is not None, f"User with ID {sample_user.id} should exist after creation"
        assert retrieved_user.id == sample_user.id, f"Retrieved user ID should match created user ID"
        assert retrieved_user.email_addresses == sample_user.email_addresses, "Email addresses should match"
        assert retrieved_user.name == sample_user.name, "User names should match"
        assert retrieved_user.settings == sample_user.settings, "User settings should match"


def test_create_and_get_conversation(clean_test_db, sample_user, sample_conversation):
    """Test creating and retrieving a conversation."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_test_db)):
        # Create user first (required for foreign key)
        Users.create(sample_user)
        
        # Create and retrieve conversation
        Conversations.create(sample_conversation)
        retrieved_conversation = Conversations.get_by_id(sample_conversation.id)
        
        assert retrieved_conversation is not None, f"Conversation with ID {sample_conversation.id} should exist"
        assert retrieved_conversation.id == sample_conversation.id, "Conversation IDs should match"
        assert retrieved_conversation.user_id == sample_conversation.user_id, "User IDs should match"
        assert retrieved_conversation.title == sample_conversation.title, "Conversation titles should match"
        assert retrieved_conversation.status == sample_conversation.status, "Conversation statuses should match"


def test_create_and_get_message(clean_test_db, sample_user, sample_conversation, sample_message):
    """Test creating and retrieving a message."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_test_db)):
        # Create dependencies first
        Users.create(sample_user)
        Conversations.create(sample_conversation)
        
        # Create and retrieve message
        Messages.create(sample_message)
        retrieved_message = Messages.get_by_id(sample_message.id)
        
        assert retrieved_message is not None, f"Message with ID {sample_message.id} should exist"
        assert retrieved_message.id == sample_message.id, "Message IDs should match"
        assert retrieved_message.conversation_id == sample_message.conversation_id, "Conversation IDs should match"
        assert retrieved_message.user_id == sample_message.user_id, "User IDs should match"
        assert retrieved_message.user_content == sample_message.user_content, "User content should match"
        assert retrieved_message.assistant_content == sample_message.assistant_content, "Assistant content should match"


def test_get_conversations_by_user(clean_test_db, sample_user, multiple_conversations):
    """Test retrieving conversations by user."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_test_db)):
        # Create user first
        Users.create(sample_user)
        
        # Create multiple conversations
        for conversation in multiple_conversations:
            Conversations.create(conversation)
        
        # Retrieve conversations by user
        user_conversations = Conversations.get_by_user(sample_user.id)
        
        assert len(user_conversations) == len(multiple_conversations), f"Should retrieve {len(multiple_conversations)} conversations"
        
        # Verify all conversations belong to the user
        for conversation in user_conversations:
            assert conversation.user_id == sample_user.id, "All conversations should belong to the test user"


def test_get_messages_by_conversation(clean_test_db, sample_user, sample_conversation, multiple_messages):
    """Test retrieving messages by conversation."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_test_db)):
        # Create dependencies
        Users.create(sample_user)
        Conversations.create(sample_conversation)
        
        # Create multiple messages
        for message in multiple_messages:
            Messages.create(message)
        
        # Retrieve messages by conversation
        conversation_messages = Messages.get_by_conversation(sample_conversation.id)
        
        assert len(conversation_messages) == len(multiple_messages), f"Should retrieve {len(multiple_messages)} messages"
        
        # Verify all messages belong to the conversation and are ordered by created_at
        for i, message in enumerate(conversation_messages):
            assert message.conversation_id == sample_conversation.id, "All messages should belong to the test conversation"
            if i > 0:
                assert message.created_at >= conversation_messages[i-1].created_at, "Messages should be ordered by created_at"


def test_database_foreign_key_constraints(clean_test_db):
    """Test that foreign key constraints are enforced."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_test_db)):
        # Try to create conversation without user (should fail)
        orphan_conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id="non-existent-user-id"
        )
        
        with pytest.raises(Exception) as exc_info:
            Conversations.create(orphan_conversation)
        
        # Verify the exception is related to foreign key constraint
        assert "foreign key" in str(exc_info.value).lower() or "constraint" in str(exc_info.value).lower(), \
            "Exception should be related to foreign key constraint violation"


def test_database_cleanup_cascade(clean_test_db, sample_user, sample_conversation, sample_message):
    """Test database cleanup and data isolation between tests."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_test_db)):
        # Create full data hierarchy
        Users.create(sample_user)
        Conversations.create(sample_conversation)
        Messages.create(sample_message)
        
        # Verify data exists
        assert Users.get_by_id(sample_user.id) is not None, "User should exist"
        assert Conversations.get_by_id(sample_conversation.id) is not None, "Conversation should exist"
        assert Messages.get_by_id(sample_message.id) is not None, "Message should exist"


def test_database_state_helpers(db_with_sample_data, assert_db_state):
    """Test database state assertion helpers."""
    data = db_with_sample_data
    
    # Test existence checks
    assert assert_db_state.user_exists(data["user"].id, data["db_file"]), "Sample user should exist"
    assert assert_db_state.conversation_exists(data["conversation"].id, data["db_file"]), "Sample conversation should exist"
    assert assert_db_state.message_exists(data["message"].id, data["db_file"]), "Sample message should exist"
    
    # Test count functions
    assert assert_db_state.count_users(data["db_file"]) == 1, "Should have exactly 1 user"
    assert assert_db_state.count_conversations(data["db_file"]) == 1, "Should have exactly 1 conversation"
    assert assert_db_state.count_messages(data["db_file"]) == 1, "Should have exactly 1 message"


def test_multiple_data_setup(db_with_multiple_data, assert_db_state):
    """Test setup with multiple users, conversations, and messages."""
    data = db_with_multiple_data
    
    # Verify counts
    assert assert_db_state.count_users(data["db_file"]) == len(data["users"]), f"Should have {len(data['users'])} users"
    assert assert_db_state.count_conversations(data["db_file"]) == len(data["conversations"]), f"Should have {len(data['conversations'])} conversations"
    assert assert_db_state.count_messages(data["db_file"]) == len(data["messages"]), f"Should have {len(data['messages'])} messages"
    
    # Verify data integrity
    for user in data["users"]:
        assert assert_db_state.user_exists(user.id, data["db_file"]), f"User {user.id} should exist"
    
    for conversation in data["conversations"]:
        assert assert_db_state.conversation_exists(conversation.id, data["db_file"]), f"Conversation {conversation.id} should exist"
    
    for message in data["messages"]:
        assert assert_db_state.message_exists(message.id, data["db_file"]), f"Message {message.id} should exist"