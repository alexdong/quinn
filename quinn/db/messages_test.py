"""Tests for messages database operations."""

import uuid
from unittest.mock import patch

import pytest

from quinn.db.messages import Message, Messages


def test_message_model_creation():
    """Test Message model creation with required fields."""
    message_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    message = Message(
        id=message_id,
        conversation_id=conversation_id,
        user_id=user_id
    )
    
    assert message.id == message_id
    assert message.conversation_id == conversation_id
    assert message.user_id == user_id
    assert message.system_prompt == ""
    assert message.user_content == ""
    assert message.assistant_content == ""
    assert message.metadata is None
    assert isinstance(message.created_at, int)
    assert isinstance(message.last_updated_at, int)


def test_message_model_with_content():
    """Test Message model with content fields."""
    message_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    message = Message(
        id=message_id,
        conversation_id=conversation_id,
        user_id=user_id,
        system_prompt="You are a helpful assistant",
        user_content="Hello, how are you?",
        assistant_content="I'm doing well, thank you!"
    )
    
    assert message.system_prompt == "You are a helpful assistant"
    assert message.user_content == "Hello, how are you?"
    assert message.assistant_content == "I'm doing well, thank you!"


def test_message_with_null_metadata():
    """Test Message model with null metadata."""
    message_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    message = Message(
        id=message_id,
        conversation_id=conversation_id,
        user_id=user_id,
        metadata=None
    )
    
    assert message.metadata is None


def test_message_json_metadata_serialization():
    """Test Message model with complex metadata."""
    message_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    metadata = {
        "tokens_used": 25,
        "cost_usd": 0.001,
        "response_time_ms": 500,
        "model_used": "gpt-4",
        "prompt_version": "v240715-120000",
        "additional_info": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    
    message = Message(
        id=message_id,
        conversation_id=conversation_id,
        user_id=user_id,
        metadata=metadata
    )
    
    assert message.metadata == metadata
    assert message.metadata is not None
    assert message.metadata["tokens_used"] == 25
    assert message.metadata["additional_info"]["temperature"] == 0.7


def test_create_message(setup_test_data, test_message_data):
    """Test creating a new message."""
    message = Message(**test_message_data)
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Messages.create(message)
        
        # Verify message was created
        retrieved_message = Messages.get_by_id(test_message_data["id"])
        assert retrieved_message is not None
        assert retrieved_message.id == test_message_data["id"]
        assert retrieved_message.conversation_id == test_message_data["conversation_id"]
        assert retrieved_message.user_id == test_message_data["user_id"]
        assert retrieved_message.system_prompt == test_message_data["system_prompt"]
        assert retrieved_message.user_content == test_message_data["user_content"]
        assert retrieved_message.assistant_content == test_message_data["assistant_content"]
        assert retrieved_message.metadata == test_message_data["metadata"]


def test_get_message_by_id(setup_test_data, test_message_data):
    """Test retrieving a message by ID."""
    message = Message(**test_message_data)
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Messages.create(message)
        
        retrieved_message = Messages.get_by_id(test_message_data["id"])
        assert retrieved_message is not None
        assert retrieved_message.id == test_message_data["id"]
        assert retrieved_message.conversation_id == test_message_data["conversation_id"]
        assert retrieved_message.user_id == test_message_data["user_id"]


def test_get_message_by_id_not_found(clean_db):
    """Test retrieving a non-existent message."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        retrieved_message = Messages.get_by_id("non-existent-id")
        assert retrieved_message is None


def test_get_messages_by_conversation(setup_test_data, test_message_data):
    """Test retrieving all messages for a conversation."""
    conversation_id = setup_test_data["conversation"]["id"]
    user_id = setup_test_data["user"]["id"]
    
    # Create first message
    message1 = Message(**test_message_data)
    
    # Create second message
    message2_id = str(uuid.uuid4())
    message2 = Message(
        id=message2_id,
        conversation_id=conversation_id,
        user_id=user_id,
        user_content="Follow-up question",
        assistant_content="Follow-up answer"
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Messages.create(message1)
        Messages.create(message2)
        
        # Get all messages for conversation
        messages = Messages.get_by_conversation(conversation_id)
        assert len(messages) == 2
        
        # Verify messages are ordered by created_at
        assert messages[0].created_at <= messages[1].created_at
        
        # Verify both messages are returned
        message_ids = [msg.id for msg in messages]
        assert test_message_data["id"] in message_ids
        assert message2_id in message_ids


def test_message_ordering_by_created_at(setup_test_data):
    """Test that messages are returned in chronological order."""
    conversation_id = setup_test_data["conversation"]["id"]
    user_id = setup_test_data["user"]["id"]
    
    # Create messages with different timestamps
    import time
    
    message1 = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        user_id=user_id,
        user_content="First message",
        created_at=int(time.time()) - 100  # 100 seconds ago
    )
    
    message2 = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        user_id=user_id,
        user_content="Second message",
        created_at=int(time.time()) - 50   # 50 seconds ago
    )
    
    message3 = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        user_id=user_id,
        user_content="Third message",
        created_at=int(time.time())        # Now
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        # Create messages in random order
        Messages.create(message2)
        Messages.create(message1)
        Messages.create(message3)
        
        # Retrieve messages
        messages = Messages.get_by_conversation(conversation_id)
        assert len(messages) == 3
        
        # Verify chronological order
        assert messages[0].user_content == "First message"
        assert messages[1].user_content == "Second message"
        assert messages[2].user_content == "Third message"


def test_update_message(setup_test_data, test_message_data):
    """Test updating an existing message."""
    import time
    
    message = Message(**test_message_data)
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Messages.create(message)
        
        original_updated_at = message.last_updated_at
        
        # Wait a moment to ensure different timestamp
        time.sleep(0.001)
        
        # Update message data
        message.system_prompt = "Updated system prompt"
        message.user_content = "Updated user content"
        message.assistant_content = "Updated assistant content"
        message.metadata = {"updated": True, "version": 2}
        
        Messages.update(message)
        
        # Verify updates
        retrieved_message = Messages.get_by_id(test_message_data["id"])
        assert retrieved_message is not None
        assert retrieved_message.system_prompt == "Updated system prompt"
        assert retrieved_message.user_content == "Updated user content"
        assert retrieved_message.assistant_content == "Updated assistant content"
        assert retrieved_message.metadata == {"updated": True, "version": 2}
        assert retrieved_message.last_updated_at >= original_updated_at


def test_delete_message(setup_test_data, test_message_data):
    """Test deleting a message."""
    message = Message(**test_message_data)
    
    with patch("quinn.db.database.DATABASE_FILE", str(setup_test_data["db_file"])):
        Messages.create(message)
        
        # Verify message exists
        retrieved_message = Messages.get_by_id(test_message_data["id"])
        assert retrieved_message is not None
        
        # Delete message
        Messages.delete(test_message_data["id"])
        
        # Verify message is deleted
        retrieved_message = Messages.get_by_id(test_message_data["id"])
        assert retrieved_message is None