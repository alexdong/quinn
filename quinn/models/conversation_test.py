"""Tests for Message and Conversation models."""

import uuid
from datetime import UTC, datetime

import pytest

from .conversation import Conversation, Message


def test_message_default_values() -> None:
    """Test Message model with default values."""
    message = Message(content="Hello world")
    assert message.role == "user"
    assert message.content == "Hello world"
    assert message.metadata == {}
    assert isinstance(message.id, str)
    assert len(message.id) == 36  # UUID4 length
    assert isinstance(message.timestamp, datetime)


def test_message_custom_values() -> None:
    """Test Message model with custom values."""
    custom_time = datetime.now(UTC)
    custom_metadata = {"key": "value", "number": 42}
    
    message = Message(
        role="assistant",
        content="AI response",
        timestamp=custom_time,
        metadata=custom_metadata,
    )
    assert message.role == "assistant"
    assert message.content == "AI response"
    assert message.timestamp == custom_time
    assert message.metadata == custom_metadata


def test_message_uuid_generation() -> None:
    """Test Message UUID generation is unique."""
    message1 = Message(content="Test 1")
    message2 = Message(content="Test 2")
    assert message1.id != message2.id
    assert uuid.UUID(message1.id)  # Should not raise
    assert uuid.UUID(message2.id)  # Should not raise


def test_message_empty_content_validation() -> None:
    """Test Message empty content validation."""
    with pytest.raises(ValueError, match="Message content cannot be empty"):
        Message(content="")
    with pytest.raises(ValueError, match="Message content cannot be empty"):
        Message(content="   ")


def test_message_metadata_types() -> None:
    """Test Message metadata supports various types."""
    metadata = {
        "string": "value",
        "int": 42,
        "float": 3.14,
        "bool": True,
    }
    message = Message(content="Test", metadata=metadata)
    assert message.metadata == metadata


def test_conversation_default_values() -> None:
    """Test Conversation model with default values."""
    conversation = Conversation()
    assert conversation.messages == []
    assert conversation.metrics is None
    assert isinstance(conversation.id, str)
    assert len(conversation.id) == 36  # UUID4 length
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_conversation_add_message() -> None:
    """Test Conversation add_message method."""
    conversation = Conversation()
    original_updated_at = conversation.updated_at
    
    message = Message(content="Hello")
    conversation.add_message(message)
    
    assert len(conversation.messages) == 1
    assert conversation.messages[0] == message
    assert conversation.updated_at > original_updated_at


def test_conversation_get_latest_message() -> None:
    """Test Conversation get_latest_message method."""
    conversation = Conversation()
    assert conversation.get_latest_message() is None
    
    message1 = Message(content="First")
    message2 = Message(content="Second")
    
    conversation.add_message(message1)
    assert conversation.get_latest_message() == message1
    
    conversation.add_message(message2)
    assert conversation.get_latest_message() == message2


def test_conversation_get_messages_by_role() -> None:
    """Test Conversation get_messages_by_role method."""
    conversation = Conversation()
    
    user_msg1 = Message(content="User 1", role="user")
    assistant_msg = Message(content="Assistant", role="assistant")
    user_msg2 = Message(content="User 2", role="user")
    
    conversation.add_message(user_msg1)
    conversation.add_message(assistant_msg)
    conversation.add_message(user_msg2)
    
    user_messages = conversation.get_messages_by_role("user")
    assistant_messages = conversation.get_messages_by_role("assistant")
    
    assert len(user_messages) == 2
    assert len(assistant_messages) == 1
    assert user_messages == [user_msg1, user_msg2]
    assert assistant_messages == [assistant_msg]


def test_conversation_uuid_generation() -> None:
    """Test Conversation UUID generation is unique."""
    conv1 = Conversation()
    conv2 = Conversation()
    assert conv1.id != conv2.id
    assert uuid.UUID(conv1.id)  # Should not raise
    assert uuid.UUID(conv2.id)  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])