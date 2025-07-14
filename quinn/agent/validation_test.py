"""Test prompt context validation."""

from datetime import UTC, datetime

import pytest

from quinn.models import Message, PromptContext

from .validation import validate_prompt_context


def test_validate_prompt_context_success() -> None:
    """Test successful prompt context validation."""
    
    message = Message(
        content="Hello, how are you?",
        role="user",
        timestamp=datetime.now(UTC),
    )
    
    context = PromptContext(
        user_input="This is a test input with enough characters",
        conversation_history=[message],
        prompt_version="v1.0",
        system_prompt="You are a helpful AI assistant that provides accurate information.",
    )
    
    # Should not raise any exceptions
    validate_prompt_context(context)


def test_validate_prompt_context_type_validation() -> None:
    """Test prompt context type validation."""
    
    with pytest.raises(AssertionError, match="Context must be PromptContext instance"):
        validate_prompt_context("not-a-context")  # type: ignore


def test_validate_prompt_context_user_input_too_short() -> None:
    """Test validation fails for too short user input."""
    
    context = PromptContext(
        user_input="short",  # Less than 10 characters
        conversation_history=[],
        prompt_version="v1.0",
        system_prompt="You are a helpful AI assistant that provides accurate information.",
    )
    
    with pytest.raises(AssertionError, match="User input too short"):
        validate_prompt_context(context)


def test_validate_prompt_context_system_prompt_too_short() -> None:
    """Test validation fails for too short system prompt."""
    
    context = PromptContext(
        user_input="This is a test input with enough characters",
        conversation_history=[],
        prompt_version="v1.0",
        system_prompt="Short",  # Less than 50 characters
    )
    
    with pytest.raises(AssertionError, match="System prompt too short"):
        validate_prompt_context(context)


def test_validate_prompt_context_empty_message_content() -> None:
    """Test that Pydantic validation prevents empty message content."""
    
    from pydantic import ValidationError
    
    # Pydantic should prevent creating a message with empty content
    with pytest.raises(ValidationError, match="Message content cannot be empty"):
        Message(
            content="",  # Empty content
            role="user",
            timestamp=datetime.now(UTC),
        )


def test_validate_prompt_context_invalid_message_role() -> None:
    """Test that Pydantic validation prevents invalid message roles."""
    
    from pydantic import ValidationError
    
    # Pydantic should prevent creating a message with invalid role
    with pytest.raises(ValidationError, match="Input should be 'user' or 'assistant'"):
        Message(
            content="Hello, how are you?",
            role="invalid_role",  # type: ignore
            timestamp=datetime.now(UTC),
        )


def test_validate_prompt_context_empty_history() -> None:
    """Test validation works with empty conversation history."""
    
    context = PromptContext(
        user_input="This is a test input with enough characters",
        conversation_history=[],  # Empty history
        prompt_version="v1.0",
        system_prompt="You are a helpful AI assistant that provides accurate information.",
    )
    
    # Should not raise any exceptions
    validate_prompt_context(context)


def test_validate_prompt_context_multiple_messages() -> None:
    """Test validation works with multiple messages in history."""
    
    message1 = Message(
        content="Hello, how are you?",
        role="user",
        timestamp=datetime.now(UTC),
    )
    
    message2 = Message(
        content="I'm doing well, thank you for asking!",
        role="assistant",
        timestamp=datetime.now(UTC),
    )
    
    context = PromptContext(
        user_input="This is a test input with enough characters",
        conversation_history=[message1, message2],
        prompt_version="v1.0",
        system_prompt="You are a helpful AI assistant that provides accurate information.",
    )
    
    # Should not raise any exceptions
    validate_prompt_context(context)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])