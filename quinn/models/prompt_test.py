"""Tests for PromptContext model."""

import uuid

import pytest

from .conversation import Message
from .prompt import PromptContext


def test_prompt_context_default_values() -> None:
    """Test PromptContext model with default values."""
    context = PromptContext(
        user_input="Hello",
        prompt_version="240715-120000",
        system_prompt="You are helpful",
    )
    assert context.user_input == "Hello"
    assert context.prompt_version == "240715-120000"
    assert context.system_prompt == "You are helpful"
    assert context.conversation_history == []
    assert isinstance(context.id, str)
    assert len(context.id) == 36  # UUID4 length


def test_prompt_context_with_conversation_history() -> None:
    """Test PromptContext with conversation history."""
    messages = [
        Message(content="Hello", role="user"),
        Message(content="Hi there!", role="assistant"),
    ]
    
    context = PromptContext(
        user_input="How are you?",
        conversation_history=messages,
        prompt_version="240715-120000",
        system_prompt="You are helpful",
    )
    assert context.conversation_history == messages


def test_prompt_context_empty_field_validation() -> None:
    """Test PromptContext empty field validation."""
    with pytest.raises(ValueError, match="Field cannot be empty"):
        PromptContext(user_input="", prompt_version="240715-120000", system_prompt="test")
    
    with pytest.raises(ValueError, match="Prompt version cannot be empty"):
        PromptContext(user_input="test", prompt_version="", system_prompt="test")
    
    with pytest.raises(ValueError, match="Field cannot be empty"):
        PromptContext(user_input="test", prompt_version="240715-120000", system_prompt="")


def test_prompt_context_whitespace_validation() -> None:
    """Test PromptContext whitespace validation."""
    with pytest.raises(ValueError, match="Field cannot be empty"):
        PromptContext(user_input="   ", prompt_version="240715-120000", system_prompt="test")


def test_prompt_context_uuid_generation() -> None:
    """Test PromptContext UUID generation is unique."""
    context1 = PromptContext(user_input="test1", prompt_version="240715-120000", system_prompt="test")
    context2 = PromptContext(user_input="test2", prompt_version="240715-120000", system_prompt="test")
    assert context1.id != context2.id
    assert uuid.UUID(context1.id)  # Should not raise
    assert uuid.UUID(context2.id)  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])