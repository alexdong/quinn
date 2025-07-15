"""Tests for conversations database operations."""

import uuid
from unittest.mock import patch

import pytest

from quinn.db.conversations import DbConversation, Conversations


def test_conversation_model_creation():
    """Test DbConversation model creation with required fields."""
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    conversation = DbConversation(conversation_id=conversation_id, user_id=user_id)
    
    assert conversation.id == conversation_id
    assert conversation.user_id == user_id
    assert conversation.title is None
    assert conversation.status == "active"
    assert conversation.total_cost == 0.0
    assert conversation.message_count == 0
    assert conversation.metadata is None


def test_conversation_model_with_optional_fields():
    """Test DbConversation model with optional fields."""
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    conversation = DbConversation(
        conversation_id=conversation_id,
        user_id=user_id,
        title="Test Conversation",
        status="archived",
        total_cost=1.5,
        message_count=5,
        metadata={"test": "data"}
    )
    
    assert conversation.title == "Test Conversation"
    assert conversation.status == "archived"
    assert conversation.total_cost == 1.5
    assert conversation.message_count == 5
    assert conversation.metadata == {"test": "data"}


def test_conversations_create(setup_test_data):
    """Test creating a conversation in the database."""
    test_conversation_data = setup_test_data["test_conversation_data"]
    
    conversation = DbConversation(
        conversation_id=test_conversation_data["id"],
        user_id=test_conversation_data["user_id"],
        title=test_conversation_data["title"],
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Conversations.create(conversation)
        
        # Verify conversation was created
        retrieved_conversation = Conversations.get_by_id(test_conversation_data["id"])
        assert retrieved_conversation is not None
        assert retrieved_conversation.id == test_conversation_data["id"]
        assert retrieved_conversation.user_id == test_conversation_data["user_id"]
        assert retrieved_conversation.title == test_conversation_data["title"]


def test_conversations_get_by_id(setup_test_data):
    """Test retrieving a conversation by ID."""
    test_conversation_data = setup_test_data["test_conversation_data"]
    
    conversation = DbConversation(
        conversation_id=test_conversation_data["id"],
        user_id=test_conversation_data["user_id"],
        title=test_conversation_data["title"],
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Conversations.create(conversation)
        
        retrieved_conversation = Conversations.get_by_id(test_conversation_data["id"])
        assert retrieved_conversation is not None
        assert retrieved_conversation.id == test_conversation_data["id"]
        assert retrieved_conversation.user_id == test_conversation_data["user_id"]


def test_conversations_get_by_user(setup_test_data):
    """Test retrieving conversations by user."""
    user_id = str(uuid.uuid4())
    
    conversation1 = DbConversation(
        conversation_id=str(uuid.uuid4()),
        user_id=user_id,
        title="First conversation",
    )
    conversation2 = DbConversation(
        conversation_id=str(uuid.uuid4()),
        user_id=user_id,
        title="Second conversation",
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Conversations.create(conversation1)
        Conversations.create(conversation2)
        
        # Retrieve conversations for user
        retrieved_conversations = Conversations.get_by_user(user_id)
        
        assert len(retrieved_conversations) == 2
        conversation_titles = [c.title for c in retrieved_conversations]
        assert "First conversation" in conversation_titles
        assert "Second conversation" in conversation_titles


def test_conversations_update(setup_test_data):
    """Test updating a conversation."""
    test_conversation_data = setup_test_data["test_conversation_data"]
    
    conversation = DbConversation(
        conversation_id=test_conversation_data["id"],
        user_id=test_conversation_data["user_id"],
        title=test_conversation_data["title"],
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Conversations.create(conversation)
        
        # Update the conversation
        conversation.title = "Updated title"
        conversation.status = "completed"
        conversation.total_cost = 2.5
        
        Conversations.update(conversation)
        
        # Verify the update
        retrieved_conversation = Conversations.get_by_id(test_conversation_data["id"])
        assert retrieved_conversation is not None
        assert retrieved_conversation.title == "Updated title"
        assert retrieved_conversation.status == "completed"
        assert retrieved_conversation.total_cost == 2.5


def test_conversations_delete(setup_test_data):
    """Test deleting a conversation."""
    test_conversation_data = setup_test_data["test_conversation_data"]
    
    conversation = DbConversation(
        conversation_id=test_conversation_data["id"],
        user_id=test_conversation_data["user_id"],
        title=test_conversation_data["title"],
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Conversations.create(conversation)
        
        # Verify conversation exists
        retrieved_conversation = Conversations.get_by_id(test_conversation_data["id"])
        assert retrieved_conversation is not None
        
        # Delete the conversation
        Conversations.delete(test_conversation_data["id"])
        
        # Verify deletion
        deleted_conversation = Conversations.get_by_id(test_conversation_data["id"])
        assert deleted_conversation is None


def test_conversations_error_handling():
    """Test error handling in conversation operations."""
    conversation_id = str(uuid.uuid4())
    
    conversation = DbConversation(
        conversation_id=conversation_id,
        user_id="test-user",
        title="Test conversation"
    )
    
    # Test database connection error
    with patch("quinn.db.conversations.get_db_connection", side_effect=Exception("Database error")):
        with pytest.raises(Exception, match="Database error"):
            Conversations.create(conversation)
        
        with pytest.raises(Exception, match="Database error"):
            Conversations.get_by_id(conversation_id)
        
        with pytest.raises(Exception, match="Database error"):
            Conversations.get_by_user("test-user")
        
        with pytest.raises(Exception, match="Database error"):
            Conversations.update(conversation)
        
        with pytest.raises(Exception, match="Database error"):
            Conversations.delete(conversation_id)