"""Tests for ConversationMetrics and AgentResponse models."""

import uuid

import pytest

from .response import AgentResponse, ConversationMetrics


def test_conversation_metrics_default_values() -> None:
    """Test ConversationMetrics model with default values."""
    metrics = ConversationMetrics(model_used="gpt-4", prompt_version="240715-120000")
    assert metrics.total_tokens_used == 0
    assert metrics.total_cost_usd == 0.0
    assert metrics.average_response_time_ms == 0
    assert metrics.message_count == 0
    assert metrics.model_used == "gpt-4"
    assert metrics.prompt_version == "240715-120000"


def test_conversation_metrics_custom_values() -> None:
    """Test ConversationMetrics model with custom values."""
    metrics = ConversationMetrics(
        total_tokens_used=1500,
        total_cost_usd=0.025,
        average_response_time_ms=750,
        message_count=3,
        model_used="claude-3.5-sonnet",
        prompt_version="240716-130000",
    )
    assert metrics.total_tokens_used == 1500
    assert metrics.total_cost_usd == 0.025
    assert metrics.average_response_time_ms == 750
    assert metrics.message_count == 3
    assert metrics.model_used == "claude-3.5-sonnet"
    assert metrics.prompt_version == "240716-130000"


def test_conversation_metrics_negative_value_validation() -> None:
    """Test ConversationMetrics negative value validation."""
    with pytest.raises(ValueError):
        ConversationMetrics(total_tokens_used=-1, model_used="gpt-4", prompt_version="240715-120000")
    
    with pytest.raises(ValueError):
        ConversationMetrics(total_cost_usd=-0.01, model_used="gpt-4", prompt_version="240715-120000")
    
    with pytest.raises(ValueError):
        ConversationMetrics(average_response_time_ms=-1, model_used="gpt-4", prompt_version="240715-120000")
    
    with pytest.raises(ValueError):
        ConversationMetrics(message_count=-1, model_used="gpt-4", prompt_version="240715-120000")


def test_conversation_metrics_empty_string_validation() -> None:
    """Test ConversationMetrics empty string validation."""
    with pytest.raises(ValueError, match="Field cannot be empty"):
        ConversationMetrics(model_used="", prompt_version="240715-120000")
    
    with pytest.raises(ValueError, match="Prompt version cannot be empty"):
        ConversationMetrics(model_used="gpt-4", prompt_version="")


def test_conversation_metrics_whitespace_validation() -> None:
    """Test ConversationMetrics whitespace validation."""
    with pytest.raises(ValueError, match="Field cannot be empty"):
        ConversationMetrics(model_used="   ", prompt_version="240715-120000")


def test_agent_response_default_values() -> None:
    """Test AgentResponse model with default values."""
    response = AgentResponse(
        content="Hello!",
        conversation_id="conv-123",
        message_id="msg-456",
    )
    assert response.content == "Hello!"
    assert response.conversation_id == "conv-123"
    assert response.message_id == "msg-456"
    assert response.tokens_used == 0
    assert response.cost_usd == 0.0
    assert response.response_time_ms == 0
    assert response.model_used == ""
    assert response.prompt_version == ""
    assert isinstance(response.id, str)
    assert len(response.id) == 36  # UUID4 length


def test_agent_response_custom_values() -> None:
    """Test AgentResponse model with custom values."""
    response = AgentResponse(
        content="AI response here",
        conversation_id="conv-789",
        message_id="msg-101",
        tokens_used=250,
        cost_usd=0.005,
        response_time_ms=1200,
        model_used="gpt-4-turbo",
        prompt_version="240715-150000",
    )
    assert response.content == "AI response here"
    assert response.conversation_id == "conv-789"
    assert response.message_id == "msg-101"
    assert response.tokens_used == 250
    assert response.cost_usd == 0.005
    assert response.response_time_ms == 1200
    assert response.model_used == "gpt-4-turbo"
    assert response.prompt_version == "240715-150000"


def test_agent_response_negative_value_validation() -> None:
    """Test AgentResponse negative value validation."""
    with pytest.raises(ValueError):
        AgentResponse(
            content="test",
            conversation_id="conv",
            message_id="msg",
            tokens_used=-1,
        )
    
    with pytest.raises(ValueError):
        AgentResponse(
            content="test",
            conversation_id="conv",
            message_id="msg",
            cost_usd=-0.01,
        )
    
    with pytest.raises(ValueError):
        AgentResponse(
            content="test",
            conversation_id="conv",
            message_id="msg",
            response_time_ms=-1,
        )


def test_agent_response_empty_string_validation() -> None:
    """Test AgentResponse empty string validation."""
    with pytest.raises(ValueError, match="Field cannot be empty"):
        AgentResponse(content="", conversation_id="conv", message_id="msg")
    
    with pytest.raises(ValueError, match="Field cannot be empty"):
        AgentResponse(content="test", conversation_id="", message_id="msg")
    
    with pytest.raises(ValueError, match="Field cannot be empty"):
        AgentResponse(content="test", conversation_id="conv", message_id="")


def test_agent_response_whitespace_validation() -> None:
    """Test AgentResponse whitespace validation."""
    with pytest.raises(ValueError, match="Field cannot be empty"):
        AgentResponse(content="   ", conversation_id="conv", message_id="msg")


def test_agent_response_uuid_generation() -> None:
    """Test AgentResponse UUID generation is unique."""
    response1 = AgentResponse(content="test1", conversation_id="conv", message_id="msg")
    response2 = AgentResponse(content="test2", conversation_id="conv", message_id="msg")
    assert response1.id != response2.id
    assert uuid.UUID(response1.id)  # Should not raise
    assert uuid.UUID(response2.id)  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])