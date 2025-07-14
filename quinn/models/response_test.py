"""Tests for ConversationMetrics and MessageMetrics models."""

import uuid

import pytest

from .response import ConversationMetrics, MessageMetrics


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


def test_message_metrics_default_values() -> None:
    """Test MessageMetrics model with default values."""
    metrics = MessageMetrics(model_used="gpt-4", prompt_version="240715-120000")
    assert metrics.tokens_used == 0
    assert metrics.cost_usd == 0.0
    assert metrics.response_time_ms == 0
    assert metrics.model_used == "gpt-4"
    assert metrics.prompt_version == "240715-120000"


def test_message_metrics_custom_values() -> None:
    """Test MessageMetrics model with custom values."""
    metrics = MessageMetrics(
        tokens_used=250,
        cost_usd=0.005,
        response_time_ms=1200,
        model_used="gpt-4-turbo",
        prompt_version="240715-150000",
    )
    assert metrics.tokens_used == 250
    assert metrics.cost_usd == 0.005
    assert metrics.response_time_ms == 1200
    assert metrics.model_used == "gpt-4-turbo"
    assert metrics.prompt_version == "240715-150000"


def test_message_metrics_negative_value_validation() -> None:
    """Test MessageMetrics negative value validation."""
    with pytest.raises(ValueError):
        MessageMetrics(tokens_used=-1, model_used="gpt-4", prompt_version="240715-120000")
    
    with pytest.raises(ValueError):
        MessageMetrics(cost_usd=-0.01, model_used="gpt-4", prompt_version="240715-120000")
    
    with pytest.raises(ValueError):
        MessageMetrics(response_time_ms=-1, model_used="gpt-4", prompt_version="240715-120000")


def test_message_metrics_empty_string_validation() -> None:
    """Test MessageMetrics empty string validation."""
    with pytest.raises(ValueError, match="Field cannot be empty"):
        MessageMetrics(model_used="", prompt_version="240715-120000")


def test_message_metrics_whitespace_validation() -> None:
    """Test MessageMetrics whitespace validation."""
    with pytest.raises(ValueError, match="Field cannot be empty"):
        MessageMetrics(model_used="   ", prompt_version="240715-120000")




if __name__ == "__main__":
    pytest.main([__file__, "-v"])