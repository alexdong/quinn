"""Tests for conversations database operations."""

import uuid
from unittest.mock import patch

import pytest

from quinn.db.conversations import Conversation, Conversations


def test_conversation_model_creation():
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
    assert isinstance(conversation.created_at, int)
    assert isinstance(conversation.updated_at, int)


def test_conversation_model_with_metadata():
    """Test Conversation model with metadata."""
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    metadata = {"topic": "testing", "priority": "high"}
    
    conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        title="Test Conversation",
        status="active",
        total_cost=0.05,
        message_count=3,
        metadata=metadata
    )
    
    assert conversation.metadata == metadata
    assert conversation.title == "Test Conversation"
    assert conversation.total_cost == 0.05
    assert conversation.message_count == 3


def test_conversation_with_null_metadata():
    """Test Conversation model with null metadata."""
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        metadata=None
    )
    
    assert conversation.metadata is None


def test_create_conversation(setup_test_data):
    """Test creating a new conversation."""
    conversation_id = str(uuid.uuid4())
    user_id = setup_test_data["user"]["id"]
    
    conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        title="New Test Conversation",
        status="active",
        total_cost=0.02,
        message_count=1,
        metadata={"source": "test"}
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Conversations.create(conversation)
        
        # Verify conversation was created
        retrieved_conversation = Conversations.get_by_id(conversation_id)
        assert retrieved_conversation is not None
        assert retrieved_conversation.id == conversation_id
        assert retrieved_conversation.user_id == user_id
        assert retrieved_conversation.title == "New Test Conversation"
        assert retrieved_conversation.status == "active"
        assert retrieved_conversation.total_cost == 0.02
        assert retrieved_conversation.message_count == 1
        assert retrieved_conversation.metadata == {"source": "test"}


def test_get_conversation_by_id(setup_test_data):
    """Test retrieving a conversation by ID."""
    conversation_data = setup_test_data["conversation"]
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        retrieved_conversation = Conversations.get_by_id(conversation_data["id"])
        assert retrieved_conversation is not None
        assert retrieved_conversation.id == conversation_data["id"]
        assert retrieved_conversation.user_id == conversation_data["user_id"]
        assert retrieved_conversation.title == conversation_data["title"]
        assert retrieved_conversation.status == conversation_data["status"]
        assert retrieved_conversation.total_cost == conversation_data["total_cost"]
        assert retrieved_conversation.message_count == conversation_data["message_count"]


def test_get_conversation_by_id_not_found(clean_db):
    """Test retrieving a non-existent conversation."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        retrieved_conversation = Conversations.get_by_id("non-existent-id")
        assert retrieved_conversation is None


def test_get_conversations_by_user(setup_test_data):
    """Test retrieving all conversations for a user."""
    user_id = setup_test_data["user"]["id"]
    
    # Create additional conversation for the same user
    conversation2_id = str(uuid.uuid4())
    conversation2 = Conversation(
        id=conversation2_id,
        user_id=user_id,
        title="Second Conversation",
        status="archived"
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Conversations.create(conversation2)
        
        # Get all conversations for user
        conversations = Conversations.get_by_user(user_id)
        assert len(conversations) == 2
        
        # Verify both conversations are returned
        conversation_ids = [conv.id for conv in conversations]
        assert setup_test_data["conversation"]["id"] in conversation_ids
        assert conversation2_id in conversation_ids


def test_update_conversation(setup_test_data):
    """Test updating an existing conversation."""
    import time
    
    conversation_data = setup_test_data["conversation"]
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        # Get the conversation
        conversation = Conversations.get_by_id(conversation_data["id"])
        assert conversation is not None
        
        original_updated_at = conversation.updated_at
        
        # Wait a moment to ensure different timestamp
        time.sleep(0.001)
        
        # Update conversation data
        conversation.title = "Updated Title"
        conversation.status = "archived"
        conversation.total_cost = 0.10
        conversation.message_count = 5
        conversation.metadata = {"updated": True, "version": 2}
        
        Conversations.update(conversation)
        
        # Verify updates
        retrieved_conversation = Conversations.get_by_id(conversation_data["id"])
        assert retrieved_conversation is not None
        assert retrieved_conversation.title == "Updated Title"
        assert retrieved_conversation.status == "archived"
        assert retrieved_conversation.total_cost == 0.10
        assert retrieved_conversation.message_count == 5
        assert retrieved_conversation.metadata == {"updated": True, "version": 2}
        assert retrieved_conversation.updated_at >= original_updated_at


def test_delete_conversation(setup_test_data):
    """Test deleting a conversation."""
    conversation_data = setup_test_data["conversation"]
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        # Verify conversation exists
        retrieved_conversation = Conversations.get_by_id(conversation_data["id"])
        assert retrieved_conversation is not None
        
        # Delete conversation
        Conversations.delete(conversation_data["id"])
        
        # Verify conversation is deleted
        retrieved_conversation = Conversations.get_by_id(conversation_data["id"])
        assert retrieved_conversation is None

def test_conversation_operations_error_handling(clean_db):
    """Test error handling in conversation operations."""
    from unittest.mock import patch
    import pytest
    
    conversation_id = str(uuid.uuid4())
    conversation = Conversation(
        id=conversation_id,
        user_id="test-user",
        title="Test Conversation"
    )
    
    # Mock database connection to raise an exception
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


def test_delete_nonexistent_conversation(clean_db):
    """Test deleting a conversation that does not exist."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        # Should not raise an exception, just log a warning
        Conversations.delete("nonexistent-conversation-id")

