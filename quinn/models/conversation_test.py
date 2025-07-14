"""Tests for Message and Conversation models."""

import uuid
from datetime import UTC, datetime

import pytest

from .conversation import Conversation, ConversationMetrics
from .message import Message, MessageMetrics


def test_message_default_values() -> None:
    """Test Message model with default values."""
    message = Message(user_content="Hello world")
    assert message.user_content == "Hello world"
    assert message.metadata is None
    assert isinstance(message.id, str)
    assert len(message.id) == 36  # UUID4 length
    assert isinstance(message.created_at, datetime)


def test_message_custom_values() -> None:
    """Test Message model with custom values."""
    custom_time = datetime.now(UTC)
    custom_metadata = MessageMetrics(
        tokens_used=100,
        cost_usd=0.005,
        response_time_ms=750,
        model_used="claude-3.5-sonnet",
        prompt_version="240715-120000",
    )
    
    message = Message(
        assistant_content="AI response",
        created_at=custom_time,
        conversation_id="conv-123",
        metadata=custom_metadata,
    )
    assert message.assistant_content == "AI response"
    assert message.created_at == custom_time
    assert message.conversation_id == "conv-123"
    assert message.metadata == custom_metadata


def test_message_uuid_generation() -> None:
    """Test Message UUID generation is unique."""
    message1 = Message(user_content="Test 1")
    message2 = Message(user_content="Test 2")
    assert message1.id != message2.id
    assert uuid.UUID(message1.id)  # Should not raise
    assert uuid.UUID(message2.id)  # Should not raise


def test_message_empty_content_validation() -> None:
    """Test Message empty content validation."""
    with pytest.raises(ValueError, match="Message content cannot be empty"):
        Message(user_content="")
    with pytest.raises(ValueError, match="Message content cannot be empty"):
        Message(user_content="   ")


def test_message_metadata_types() -> None:
    """Test Message metadata supports MessageMetrics type."""
    metadata = MessageMetrics(
        tokens_used=42,
        cost_usd=3.14,
        response_time_ms=100,
        model_used="test-model",
        prompt_version="240715-120000",
    )
    message = Message(user_content="Test", metadata=metadata)
    assert message.metadata == metadata
    assert isinstance(message.metadata, MessageMetrics)


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
    
    message = Message(user_content="Hello")
    conversation.add_message(message)
    
    assert len(conversation.messages) == 1
    assert conversation.messages[0] == message
    assert conversation.updated_at > original_updated_at


def test_conversation_get_latest_message() -> None:
    """Test Conversation get_latest_message method."""
    conversation = Conversation()
    assert conversation.get_latest_message() is None
    
    message1 = Message(user_content="First")
    message2 = Message(user_content="Second")
    
    conversation.add_message(message1)
    assert conversation.get_latest_message() == message1
    
    conversation.add_message(message2)
    assert conversation.get_latest_message() == message2


def test_conversation_metrics_calculation() -> None:
    """Test conversation metrics calculation."""
    conv = Conversation()
    
    # No messages, metrics should be None
    assert conv.metrics is None

    # Add messages with metadata
    msg1 = Message(
        user_content="User message 1",
        metadata=MessageMetrics(
            tokens_used=50,
            cost_usd=0.001,
            response_time_ms=500,
            model_used="model-a",
            prompt_version="240715-120000",
        ),
    )
    msg2 = Message(
        assistant_content="Assistant response 1",
        metadata=MessageMetrics(
            tokens_used=100,
            cost_usd=0.002,
            response_time_ms=1000,
            model_used="model-a",
            prompt_version="240715-120000",
        ),
    )
    msg3 = Message(
        user_content="User message 2",
        metadata=MessageMetrics(
            tokens_used=75,
            cost_usd=0.0015,
            response_time_ms=750,
            model_used="model-b",
            prompt_version="240715-120000",
        ),
    )

    conv.add_message(msg1)
    conv.add_message(msg2)
    conv.add_message(msg3)

    metrics = conv.metrics
    assert metrics is not None
    assert metrics.total_tokens_used == 225  # 50 + 100 + 75
    assert metrics.total_cost_usd == pytest.approx(0.0045)  # 0.001 + 0.002 + 0.0015
    assert metrics.average_response_time_ms == 750  # (500 + 1000 + 750) / 3
    assert metrics.message_count == 3
    assert metrics.model_used == "model-b"  # Latest model
    assert metrics.prompt_version == "240715-120000"

    # Test with messages without metadata
    conv_no_metrics = Conversation()
    conv_no_metrics.add_message(Message(user_content="No metrics here"))
    assert conv_no_metrics.metrics is None


def test_conversation_uuid_generation() -> None:
    """Test Conversation UUID generation is unique."""
    conv1 = Conversation()
    conv2 = Conversation()
    assert conv1.id != conv2.id
    assert uuid.UUID(conv1.id)  # Should not raise
    assert uuid.UUID(conv2.id)  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])