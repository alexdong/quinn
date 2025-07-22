"""Tests for core AI agent functionality."""

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from quinn.agent.core import (
    MAX_PROMPT_LENGTH,
    UsageMetrics,
    _build_conversation_prompt,
    _calculate_usage_metrics,
    _load_system_prompt,
    SYSTEM_PROMPT,
    create_agent,
    generate_response,
)
from quinn.models import AgentConfig, Message
from quinn.models.message import MessageMetrics


def test_usage_metrics_creation() -> None:
    """Test UsageMetrics named tuple creation."""
    metrics = UsageMetrics(
        input_tokens=100,
        output_tokens=50,
        cached_tokens=10,
        total_tokens=150,
        total_cost_usd=0.005,
    )
    
    assert metrics.input_tokens == 100
    assert metrics.output_tokens == 50
    assert metrics.cached_tokens == 10
    assert metrics.total_tokens == 150
    assert metrics.total_cost_usd == 0.005


def test_load_system_prompt_success() -> None:
    """Test loading system prompt from file."""
    mock_content = "You are Quinn, a helpful AI assistant."
    
    with patch("pathlib.Path.read_text", return_value=f"  {mock_content}  "):
        result = _load_system_prompt()
        assert result == mock_content


def test_load_system_prompt_file_not_found() -> None:
    """Test fallback when system prompt file is not found."""
    with patch("pathlib.Path.read_text", side_effect=FileNotFoundError):
        result = _load_system_prompt()
        assert "Quinn" in result
        assert "helpful AI assistant" in result
        assert "asking thoughtful questions" in result


def test_build_conversation_prompt_no_history() -> None:
    """Test building prompt with no conversation history."""
    message = Message(user_content="Hello, how are you?")
    result = _build_conversation_prompt(message, [])
    assert result == "Hello, how are you?"


def test_build_conversation_prompt_with_history() -> None:
    """Test building prompt with conversation history."""
    history = [
        Message(
            user_content="What's the weather?",
            assistant_content="I can't check weather directly.",
        ),
        Message(
            user_content="Thanks for the info",
            assistant_content="You're welcome!",
        ),
    ]
    
    current_message = Message(user_content="What about tomorrow?")
    result = _build_conversation_prompt(current_message, history)
    
    assert "Previous conversations:" in result
    assert "User: What's the weather?" in result
    assert "Assistant: I can't check weather directly." in result
    assert "User: Thanks for the info" in result
    assert "Assistant: You're welcome!" in result
    assert "User: What about tomorrow?" in result


def test_build_conversation_prompt_partial_history() -> None:
    """Test building prompt with partial conversation history."""
    history = [
        Message(user_content="Hello"),  # No assistant content
        Message(assistant_content="Hi there!"),  # No user content
    ]
    
    current_message = Message(user_content="How are you?")
    result = _build_conversation_prompt(current_message, history)
    
    assert "User: Hello" in result
    assert "Assistant: Hi there!" in result
    assert "User: How are you?" in result


def test_calculate_usage_metrics_basic() -> None:
    """Test basic usage metrics calculation."""
    # Mock AgentRunResult
    mock_usage = MagicMock()
    mock_usage.request_tokens = 100
    mock_usage.response_tokens = 50
    mock_usage.total_tokens = 150
    mock_usage.details = None
    
    mock_result = MagicMock()
    mock_result.usage.return_value = mock_usage
    
    config = AgentConfig.o4mini()
    
    with patch("quinn.agent.core.calculate_cost", return_value=0.005):
        metrics = _calculate_usage_metrics(mock_result, config)
    
    assert metrics.input_tokens == 100
    assert metrics.output_tokens == 50
    assert metrics.cached_tokens == 0
    assert metrics.total_tokens == 150
    assert metrics.total_cost_usd == 0.005


def test_calculate_usage_metrics_with_cached_tokens() -> None:
    """Test usage metrics calculation with cached tokens."""
    mock_usage = MagicMock()
    mock_usage.request_tokens = 100
    mock_usage.response_tokens = 50
    mock_usage.total_tokens = 150
    mock_usage.details = {"cache_read_input_tokens": 25}
    
    mock_result = MagicMock()
    mock_result.usage.return_value = mock_usage
    
    config = AgentConfig.o4mini()
    
    with patch("quinn.agent.core.calculate_cost", return_value=0.005):
        metrics = _calculate_usage_metrics(mock_result, config)
    
    assert metrics.cached_tokens == 25


def test_calculate_usage_metrics_no_usage() -> None:
    """Test usage metrics calculation when no usage info available."""
    mock_result = MagicMock()
    mock_result.usage.return_value = None
    
    config = AgentConfig.o4mini()
    
    with pytest.raises(AssertionError, match="Usage information is required"):
        _calculate_usage_metrics(mock_result, config)


@pytest.mark.asyncio
async def test_create_agent() -> None:
    """Test creating agent with configuration."""
    config = AgentConfig.o4mini()
    
    with patch("quinn.agent.core.SYSTEM_PROMPT", "Test prompt"):
        with patch("quinn.agent.core.Agent") as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            result = await create_agent(config)

            assert result == mock_agent
            mock_agent_class.assert_called_once()


@pytest.mark.asyncio
async def test_create_agent_invalid_config() -> None:
    """Test creating agent with invalid configuration."""
    with pytest.raises(AssertionError, match="Config must be AgentConfig instance"):
        await create_agent("invalid_config")  # type: ignore


@pytest.mark.asyncio
async def test_generate_response_success() -> None:
    """Test successful response generation."""
    message = Message(
        user_content="Hello, how are you?",
        conversation_id=str(uuid4()),
    )
    
    # Mock the agent and its response
    mock_result = MagicMock()
    mock_result.output = "I'm doing well, thank you!"
    
    mock_usage = MagicMock()
    mock_usage.request_tokens = 10
    mock_usage.response_tokens = 8
    mock_usage.total_tokens = 18
    mock_usage.details = None
    mock_result.usage.return_value = mock_usage
    
    mock_agent = AsyncMock()
    mock_agent.run.return_value = mock_result
    
    with patch("quinn.agent.core.create_agent", return_value=mock_agent):
        with patch("quinn.agent.core.calculate_cost", return_value=0.001):
            result = await generate_response(message)
    
    assert result.user_content == "Hello, how are you?"
    assert result.assistant_content == "I'm doing well, thank you!"
    assert result.conversation_id == message.conversation_id
    assert result.metadata is not None
    assert result.metadata.tokens_used == 18
    assert result.metadata.cost_usd == 0.001
    assert result.metadata.model_used == "gemini-2.5-flash"


@pytest.mark.asyncio
async def test_generate_response_error_handling() -> None:
    """Test error handling during response generation."""
    message = Message(
        user_content="Hello",
        conversation_id=str(uuid4()),
    )
    
    mock_agent = AsyncMock()
    mock_agent.run.side_effect = Exception("API Error")
    
    with patch("quinn.agent.core.create_agent", return_value=mock_agent):
        result = await generate_response(message)
    
    assert result.user_content == "Hello"
    assert "Error generating response: API Error" in result.assistant_content
    assert result.conversation_id == message.conversation_id
    assert result.system_prompt == "Error occurred during response generation"
    assert result.metadata is None


def test_max_prompt_length_constant() -> None:
    """Test that MAX_PROMPT_LENGTH constant is reasonable."""
    assert MAX_PROMPT_LENGTH == 20000
    assert isinstance(MAX_PROMPT_LENGTH, int)
    assert MAX_PROMPT_LENGTH > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])