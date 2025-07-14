"""Tests for Message model."""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from .message import Message, MessageMetrics


def test_message_default_values() -> None:
    """Test Message model with default values."""
    message = Message(user_content="Hello world")

    assert message.user_content == "Hello world"
    assert message.assistant_content == ""
    assert message.conversation_id == ""
    assert message.system_prompt == ""
    assert message.metadata is None
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
        user_content="What is AI?",
        assistant_content="Custom message content",
        conversation_id="conv-12345",
        system_prompt="You are a helpful assistant",
        metadata=metadata,
    )

    assert message.assistant_content == "Custom message content"
    assert message.user_content == "What is AI?"
    assert message.conversation_id == "conv-12345"
    assert message.system_prompt == "You are a helpful assistant"

    assert message.metadata == metadata


def test_message_uuid_generation() -> None:
    """Test Message UUID generation is unique."""
    message1 = Message(user_content="test1")
    message2 = Message(user_content="test2")

    assert message1.id != message2.id
    assert uuid.UUID(message1.id)  # Should not raise
    assert uuid.UUID(message2.id)  # Should not raise


def test_message_empty_content_validation() -> None:
    """Test Message with empty content (should work since fields are optional)."""
    # Empty content should be allowed since all fields have defaults
    message = Message()
    assert message.user_content == ""
    assert message.assistant_content == ""


def test_message_content_fields() -> None:
    """Test Message content fields work correctly."""
    message = Message(user_content="Hello", assistant_content="Hi there!")
    assert message.user_content == "Hello"
    assert message.assistant_content == "Hi there!"


def test_message_with_system_prompt() -> None:
    """Test Message with system prompt."""
    message = Message(
        user_content="What is AI?",
        system_prompt="You are an expert AI researcher",
    )

    assert message.user_content == "What is AI?"
    assert message.system_prompt == "You are an expert AI researcher"


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
        assistant_content="Hello",
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
        user_content="Follow-up question",
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
        user_content="Test message",
        conversation_id="conv-456",
        system_prompt="Be concise",
        metadata=metadata,
    )

    data = message.model_dump()

    assert data["user_content"] == "Test message"
    assert data["conversation_id"] == "conv-456"
    assert data["system_prompt"] == "Be concise"
    assert data["metadata"]["tokens_used"] == 50


def test_message_from_dict() -> None:
    """Test Message can be created from dict."""
    data = {
        "assistant_content": "From dict",
        "conversation_id": "conv-789",
        "system_prompt": "Be helpful",
    }

    message = Message(**data)

    assert message.assistant_content == "From dict"
    assert message.conversation_id == "conv-789"
    assert message.system_prompt == "Be helpful"


if __name__ == "__main__":
    # Demonstrate Message usage
    print("Message demonstration:")

    # Basic message
    basic_message = Message(user_content="Hello, Quinn!")
    print(
        f"Basic message: {basic_message.user_content} (ID: {basic_message.id[:8]}...)"
    )

    # Message with all fields
    full_message = Message(
        user_content="What can you help me with?",
        assistant_content="How can I help you today?",
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
    print(f"Full message user: {full_message.user_content}")
    print(f"Full message assistant: {full_message.assistant_content}")
    print(f"System prompt: {full_message.system_prompt[:30]}...")
    print(f"Metadata: {full_message.metadata}")

    print("Message demonstration completed.")


def test_message_metrics_model_used_validation() -> None:
    """Test MessageMetrics model_used field validation."""
    from quinn.models.message import MessageMetrics
    import pytest
    
    # Test empty model_used field
    with pytest.raises(ValueError, match="Field cannot be empty"):
        MessageMetrics(
            tokens_used=100,
            cost_usd=0.01,
            response_time_ms=500,
            model_used="",  # Empty string should trigger validation
            prompt_version="240715-120000"
        )
    
    # Test whitespace-only model_used field  
    with pytest.raises(ValueError, match="Field cannot be empty"):
        MessageMetrics(
            tokens_used=100,
            cost_usd=0.01,
            response_time_ms=500,
            model_used="   ",  # Whitespace only should trigger validation
            prompt_version="240715-120000"
        )



def test_message_user_content_validation_empty_string() -> None:
    """Test Message user_content validation with empty string."""
    from quinn.models.message import Message
    import pytest
    
    # Test with empty string (should trigger validation)
    with pytest.raises(ValueError, match="Message content cannot be empty"):
        Message(user_content="")

