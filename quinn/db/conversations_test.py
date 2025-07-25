"""Tests for conversations database operations."""

import uuid
from unittest.mock import patch

import pytest

from quinn.db.conversations import ConversationStore
from quinn.models.conversation import Conversation


def test_conversation_model_creation() -> None:
    """Test Conversation model creation with required fields."""
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    conversation = Conversation(id=conversation_id, user_id=user_id)
    assert conversation.id == conversation_id
    assert conversation.user_id == user_id
    assert conversation.title is None
    assert conversation.status == "active"
    assert conversation.total_cost == 0.0
    assert conversation.message_count == 0
    assert conversation.metadata is None



def test_conversation_model_with_optional_fields() -> None:
    """Test Conversation model with optional fields."""
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        title="Test Conversation",
        status="archived",
        total_cost=1.5,
        message_count=5,
        metadata={"test": "data"},
    )

    assert conversation.title == "Test Conversation"
    assert conversation.status == "archived"
    assert conversation.total_cost == 1.5
    assert conversation.message_count == 5
    assert conversation.metadata == {"test": "data"}


def test_conversations_create(setup_test_data):
    """Test creating a conversation in the database."""
    # Create a new conversation with unique ID
    new_conversation_id = str(uuid.uuid4())
    user_id = setup_test_data["test_user_data"]["id"]
    
    conversation = Conversation(
        id=new_conversation_id,
        user_id=user_id,
        title="New Test Conversation",
    )

    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        ConversationStore.create(conversation)
        # Verify conversation was created
        retrieved_conversation = ConversationStore.get_by_id(new_conversation_id)
        assert retrieved_conversation is not None
        assert retrieved_conversation.id == new_conversation_id
        assert retrieved_conversation.user_id == user_id
        assert retrieved_conversation.title == "New Test Conversation"


def test_conversations_get_by_id(setup_test_data):
    """Test retrieving a conversation by ID."""
    # Use the existing conversation from setup_test_data
    test_conversation_data = setup_test_data["test_conversation_data"]

    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        retrieved_conversation = ConversationStore.get_by_id(test_conversation_data["id"])
        assert retrieved_conversation is not None
        assert retrieved_conversation.id == test_conversation_data["id"]
        assert retrieved_conversation.user_id == test_conversation_data["user_id"]
        assert retrieved_conversation.title == test_conversation_data["title"]


def test_conversations_get_by_user(setup_test_data):
    """Test retrieving conversations by user."""
    # Use existing test user to satisfy foreign key constraints
    user_id = setup_test_data["test_user_data"]["id"]
    conversation1 = Conversation(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="First conversation",
    )
    conversation2 = Conversation(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Second conversation",
    )

    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        ConversationStore.create(conversation1)
        ConversationStore.create(conversation2)
        
        # Retrieve conversations for user (includes existing test conversation)
        retrieved_conversations = ConversationStore.get_by_user(user_id)

        # Should have 3 conversations (2 new + 1 from setup_test_data)
        assert len(retrieved_conversations) == 3
        conversation_titles = [c.title for c in retrieved_conversations]
        assert "First conversation" in conversation_titles
        assert "Second conversation" in conversation_titles
        assert "Test Conversation" in conversation_titles  # From setup_test_data


def test_conversations_update(setup_test_data):
    """Test updating a conversation."""
    # Use the existing conversation from setup_test_data
    test_conversation_data = setup_test_data["test_conversation_data"]

    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        # Get the existing conversation
        conversation = ConversationStore.get_by_id(test_conversation_data["id"])
        assert conversation is not None

        # Update the conversation
        conversation.title = "Updated title"
        conversation.status = "completed"
        conversation.total_cost = 2.5
        ConversationStore.update(conversation)

        # Verify the update
        retrieved_conversation = ConversationStore.get_by_id(test_conversation_data["id"])
        assert retrieved_conversation is not None
        assert retrieved_conversation.title == "Updated title"
        assert retrieved_conversation.status == "completed"
        assert retrieved_conversation.total_cost == 2.5


def test_conversations_delete(setup_test_data):
    """Test deleting a conversation."""
    # Create a new conversation to delete
    new_conversation_id = str(uuid.uuid4())
    user_id = setup_test_data["test_user_data"]["id"]

    
    conversation = Conversation(
        id=new_conversation_id,
        user_id=user_id,
        title="Conversation to delete",
    )

    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        ConversationStore.create(conversation)
        # Verify conversation exists
        retrieved_conversation = ConversationStore.get_by_id(new_conversation_id)
        assert retrieved_conversation is not None

        # Delete the conversation
        ConversationStore.delete(new_conversation_id)
        # Verify deletion
        deleted_conversation = ConversationStore.get_by_id(new_conversation_id)
        assert deleted_conversation is None


def test_conversations_error_handling():
    """Test error handling in conversation operations."""
    conversation_id = str(uuid.uuid4())

    conversation = Conversation(
        id=conversation_id,
        user_id="test-user",
        title="Test conversation"
    )

    # Test database connection error
    with patch(
        "quinn.db.conversations.get_db_connection",
        side_effect=Exception("Database error"),
    ):
        with pytest.raises(Exception, match="Database error"):
            ConversationStore.create(conversation)
        
        with pytest.raises(Exception, match="Database error"):
            ConversationStore.get_by_id(conversation_id)
        
        with pytest.raises(Exception, match="Database error"):
            ConversationStore.get_by_user("test-user")
        
        with pytest.raises(Exception, match="Database error"):
            ConversationStore.update(conversation)
        
        with pytest.raises(Exception, match="Database error"):
            ConversationStore.delete(conversation_id)
