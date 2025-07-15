"""Tests for messages database operations."""

import uuid
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from quinn.db.messages import Messages
from quinn.models.message import Message, MessageMetrics


def test_message_model_creation():
    """Test Message model creation with required fields."""
    message_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    
    message = Message(
        id=message_id,
        conversation_id=conversation_id,
    )
    
    assert message.id == message_id
    assert message.conversation_id == conversation_id
    assert message.system_prompt == ""
    assert message.user_content == ""
    assert message.assistant_content == ""
    assert message.metadata is None
    assert isinstance(message.created_at, datetime)
    assert isinstance(message.last_updated_at, datetime)


def test_message_model_with_content():
    """Test Message model with content fields."""
    message_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    
    message = Message(
        id=message_id,
        conversation_id=conversation_id,
        system_prompt="You are a helpful assistant",
        user_content="Hello, how are you?",
        assistant_content="I'm doing well, thank you!"
    )
    
    assert message.system_prompt == "You are a helpful assistant"
    assert message.user_content == "Hello, how are you?"
    assert message.assistant_content == "I'm doing well, thank you!"


def test_message_model_with_metadata():
    """Test Message model with metadata."""
    message_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    
    metadata = MessageMetrics(
        tokens_used=25,
        cost_usd=0.0015,
        response_time_ms=1200,
        model_used="gpt-4o-mini",
        prompt_version="240715-120000"
    )
    
    message = Message(
        id=message_id,
        conversation_id=conversation_id,
        metadata=metadata
    )
    
    assert message.metadata == metadata
    assert message.metadata is not None
    assert message.metadata.tokens_used == 25
    assert message.metadata.cost_usd == 0.0015


def test_messages_create(setup_test_data):
    """Test creating a message in the database."""
    # Create a new message with unique ID
    new_message_id = str(uuid.uuid4())
    conversation_id = setup_test_data["test_conversation_data"]["id"]
    user_id = setup_test_data["test_user_data"]["id"]
    
    message = Message(
        id=new_message_id,
        conversation_id=conversation_id,
        system_prompt="You are a helpful assistant",
        user_content="Hello, how are you?",
        assistant_content="I'm doing well, thank you!",
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Messages.create(message, user_id)
        
        # Verify message was created
        retrieved_message = Messages.get_by_id(new_message_id)
        assert retrieved_message is not None
        assert retrieved_message.id == new_message_id
        assert retrieved_message.conversation_id == conversation_id
        assert retrieved_message.system_prompt == "You are a helpful assistant"
        assert retrieved_message.user_content == "Hello, how are you?"
        assert retrieved_message.assistant_content == "I'm doing well, thank you!"


def test_messages_get_by_id(setup_test_data):
    """Test retrieving a message by ID."""
    # Create a new message with unique ID
    new_message_id = str(uuid.uuid4())
    conversation_id = setup_test_data["test_conversation_data"]["id"]
    user_id = setup_test_data["test_user_data"]["id"]
    
    message = Message(
        id=new_message_id,
        conversation_id=conversation_id,
        system_prompt="You are a helpful assistant",
        user_content="Test message content",
        assistant_content="Test response content",
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Messages.create(message, user_id)
        
        retrieved_message = Messages.get_by_id(new_message_id)
        assert retrieved_message is not None
        assert retrieved_message.id == new_message_id
        assert retrieved_message.conversation_id == conversation_id


def test_messages_get_by_conversation(setup_test_data):
    """Test retrieving messages by conversation."""
    # Use existing test data to satisfy foreign key constraints
    conversation_id = setup_test_data["test_conversation_data"]["id"]
    user_id = setup_test_data["test_user_data"]["id"]
    
    # Create test messages with specific times
    now = datetime.now(UTC)
    message1 = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        user_content="First message",
        created_at=datetime.fromtimestamp(now.timestamp() - 100, UTC),  # 100 seconds ago
    )
    message2 = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        user_content="Second message",
        created_at=datetime.fromtimestamp(now.timestamp() - 50, UTC),   # 50 seconds ago
    )
    message3 = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        user_content="Third message",
        created_at=now,  # Now
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        # Create messages in random order
        Messages.create(message2, user_id)
        Messages.create(message1, user_id)
        Messages.create(message3, user_id)
        
        # Retrieve messages
        retrieved_messages = Messages.get_by_conversation(conversation_id)
        
        # Should be ordered by created_at ASC
        assert len(retrieved_messages) == 3
        assert retrieved_messages[0].user_content == "First message"
        assert retrieved_messages[1].user_content == "Second message"
        assert retrieved_messages[2].user_content == "Third message"


def test_messages_update(setup_test_data):
    """Test updating a message."""
    import time
    
    # Create a new message with unique ID
    new_message_id = str(uuid.uuid4())
    conversation_id = setup_test_data["test_conversation_data"]["id"]
    user_id = setup_test_data["test_user_data"]["id"]
    
    message = Message(
        id=new_message_id,
        conversation_id=conversation_id,
        system_prompt="Original system prompt",
        user_content="Original user content",
        assistant_content="Original assistant content",
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Messages.create(message, user_id)
        
        # Get the original timestamp from database (to avoid precision issues)
        original_message = Messages.get_by_id(new_message_id)
        assert original_message is not None
        original_updated_at = original_message.last_updated_at
        
        # Wait a moment to ensure different timestamp  
        time.sleep(1.1)  # Wait more than 1 second to ensure integer timestamp difference
        
        # Update the message
        message.system_prompt = "Updated system prompt"
        message.user_content = "Updated user content"
        message.assistant_content = "Updated assistant content"
        
        Messages.update(message)
        
        # Verify the update
        retrieved_message = Messages.get_by_id(new_message_id)
        assert retrieved_message is not None
        assert retrieved_message.system_prompt == "Updated system prompt"
        assert retrieved_message.user_content == "Updated user content"
        assert retrieved_message.assistant_content == "Updated assistant content"
        # Verify timestamp was updated (database uses second precision)
        assert retrieved_message.last_updated_at > original_updated_at


def test_messages_delete(setup_test_data):
    """Test deleting a message."""
    # Create a new message with unique ID
    new_message_id = str(uuid.uuid4())
    conversation_id = setup_test_data["test_conversation_data"]["id"]
    user_id = setup_test_data["test_user_data"]["id"]
    
    message = Message(
        id=new_message_id,
        conversation_id=conversation_id,
        system_prompt="Test system prompt",
        user_content="Test user content",
        assistant_content="Test assistant content",
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Messages.create(message, user_id)
        
        # Verify message exists
        retrieved_message = Messages.get_by_id(new_message_id)
        assert retrieved_message is not None
        
        # Delete the message
        Messages.delete(new_message_id)
        
        # Verify deletion
        deleted_message = Messages.get_by_id(new_message_id)
        assert deleted_message is None


def test_messages_error_handling():
    """Test error handling in message operations."""
    message_id = str(uuid.uuid4())
    
    message = Message(
        id=message_id,
        conversation_id="test-conv",
        user_content="Test message"
    )
    
    # Test database connection error
    with patch("quinn.db.messages.get_db_connection", side_effect=Exception("Database error")):
        with pytest.raises(Exception, match="Database error"):
            Messages.create(message, "test-user")
        
        with pytest.raises(Exception, match="Database error"):
            Messages.get_by_id(message_id)
        
        with pytest.raises(Exception, match="Database error"):
            Messages.get_by_conversation("test-conv")
        
        with pytest.raises(Exception, match="Database error"):
            Messages.update(message)
        
        with pytest.raises(Exception, match="Database error"):
            Messages.delete(message_id)