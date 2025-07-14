"""Tests for Message model."""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from .message import Message
from .response import MessageMetrics


def test_message_default_values() -> None:
    """Test Message model with default values."""
    message = Message(content="Hello world")
    
    assert message.content == "Hello world"
    assert message.role == "user"
    assert message.conversation_id == ""
    assert message.system_prompt == ""
    assert message.metadata is None
    assert isinstance(message.timestamp, datetime)
    assert uuid.UUID(message.id)  # Should not raise


def test_message_custom_values() -> None:
    """Test Message model with custom values."""
    custom_time = datetime.now(UTC)
    metadata = MessageMetrics(
        tokens_used=150,
        cost_usd=0.002,
        response_time_ms=750,
        model_used="claude-3.5-sonnet",
        prompt_version="240715-120000",
    )
    
    message = Message(
        content="Custom message content",
        role="assistant",
        conversation_id="conv-12345",
        system_prompt="You are a helpful assistant",
        timestamp=custom_time,
        metadata=metadata,
    )
    
    assert message.content == "Custom message content"
    assert message.role == "assistant"
    assert message.conversation_id == "conv-12345"
    assert message.system_prompt == "You are a helpful assistant"
    assert message.timestamp == custom_time
    assert message.metadata == metadata


def test_message_uuid_generation() -> None:
    """Test Message UUID generation is unique."""
    message1 = Message(content="test1")
    message2 = Message(content="test2")
    
    assert message1.id != message2.id
    assert uuid.UUID(message1.id)  # Should not raise
    assert uuid.UUID(message2.id)  # Should not raise


def test_message_empty_content_validation() -> None:
    """Test Message empty content validation."""
    with pytest.raises(ValidationError, match="Message content cannot be empty"):
        Message(content="")
    
    with pytest.raises(ValidationError, match="Message content cannot be empty"):
        Message(content="   ")  # Whitespace only


def test_message_invalid_role_validation() -> None:
    """Test Message invalid role validation."""
    with pytest.raises(ValidationError, match="Input should be 'user' or 'assistant'"):
        Message(content="Hello", role="invalid_role")  # type: ignore


def test_message_with_system_prompt() -> None:
    """Test Message with system prompt."""
    message = Message(
        content="What is AI?",
        role="user",
        system_prompt="You are an expert AI researcher",
    )
    
    assert message.content == "What is AI?"
    assert message.system_prompt == "You are an expert AI researcher"
    assert message.role == "user"


def test_message_with_metadata() -> None:
    """Test Message with metadata."""
    metadata = MessageMetrics(
        tokens_used=100,
        cost_usd=0.001,
        response_time_ms=500,
        model_used="claude-3.5-sonnet",
        prompt_version="240715-120000",
    )
    
    message = Message(
        content="Hello",
        role="assistant",
        metadata=metadata,
    )
    
    assert message.metadata == metadata
    assert message.metadata is not None
    assert message.metadata.tokens_used == 100
    assert message.metadata.cost_usd == 0.001


def test_message_conversation_context() -> None:
    """Test Message with conversation context."""
    conv_id = str(uuid.uuid4())
    
    message = Message(
        content="Follow-up question",
        role="user",
        conversation_id=conv_id,
        system_prompt="Continue being helpful",
    )
    
    assert message.conversation_id == conv_id
    assert message.system_prompt == "Continue being helpful"


def test_message_serialization() -> None:
    """Test Message can be serialized to dict."""
    metadata = MessageMetrics(
        tokens_used=50,
        cost_usd=0.0005,
        response_time_ms=300,
        model_used="claude-3.5-sonnet",
        prompt_version="240715-120000",
    )
    
    message = Message(
        content="Test message",
        role="user",
        conversation_id="conv-456",
        system_prompt="Be concise",
        metadata=metadata,
    )
    
    data = message.model_dump()
    
    assert data["content"] == "Test message"
    assert data["role"] == "user"
    assert data["conversation_id"] == "conv-456"
    assert data["system_prompt"] == "Be concise"
    assert data["metadata"]["tokens_used"] == 50


def test_message_from_dict() -> None:
    """Test Message can be created from dict."""
    data = {
        "content": "From dict",
        "role": "assistant",
        "conversation_id": "conv-789",
        "system_prompt": "Be helpful",
    }
    
    message = Message(**data)
    
    assert message.content == "From dict"
    assert message.role == "assistant"
    assert message.conversation_id == "conv-789"
    assert message.system_prompt == "Be helpful"


if __name__ == "__main__":
    # Demonstrate Message usage
    print("Message demonstration:")
    
    # Basic message
    basic_message = Message(content="Hello, Quinn!")
    print(f"Basic message: {basic_message.content} (ID: {basic_message.id[:8]}...)")
    
    # Message with all fields
    full_message = Message(
        content="How can I help you today?",
        role="assistant",
        conversation_id="conv-demo",
        system_prompt="You are Quinn, a helpful AI assistant",
        metadata=MessageMetrics(
            tokens_used=25,
            cost_usd=0.0003,
            response_time_ms=400,
            model_used="claude-3.5-sonnet",
            prompt_version="240715-120000",
        ),
    )
    print(f"Full message: {full_message.content}")
    print(f"System prompt: {full_message.system_prompt[:30]}...")
    print(f"Metadata: {full_message.metadata}")
    
    # Validation examples
    try:
        invalid_message = Message(content="")
    except ValidationError as e:
        print(f"Validation error: {e}")
    
    print("Message demonstration completed.")