"""Test message validation for AI processing."""

from datetime import UTC, datetime

import pytest

from quinn.models import Message

from .validation import validate_message_for_ai


def test_validate_message_for_ai_success() -> None:
    """Test successful message validation."""
    
    history_message = Message(
        user_content="Hello, how are you?",
        created_at=datetime.now(UTC),
    )
    
    message = Message(
        user_content="This is a test input with enough characters",
        system_prompt="You are a helpful AI assistant that provides accurate information.",
    )
    
    # Should not raise any exceptions
    validate_message_for_ai(message, [history_message])


def test_validate_message_for_ai_type_validation() -> None:
    """Test message type validation."""
    
    with pytest.raises(AssertionError, match="Message must be Message instance"):
        validate_message_for_ai("not-a-message")  # type: ignore


def test_validate_message_for_ai_content_too_short() -> None:
    """Test validation fails for too short message content."""
    
    message = Message(
        user_content="short",  # Less than 10 characters
        system_prompt="You are a helpful AI assistant that provides accurate information.",
    )
    
    with pytest.raises(AssertionError, match="Message content too short"):
        validate_message_for_ai(message)


def test_validate_message_for_ai_system_prompt_too_short() -> None:
    """Test validation fails for too short system prompt."""
    
    message = Message(
        user_content="This is a test input with enough characters",
        system_prompt="Short",  # Less than 50 characters
    )
    
    with pytest.raises(AssertionError, match="System prompt too short"):
        validate_message_for_ai(message)


def test_message_empty_content_validation() -> None:
    """Test that Pydantic validation prevents empty message content."""
    
    from pydantic import ValidationError
    
    # Pydantic should prevent creating a message with empty content
    with pytest.raises(ValidationError, match="Message content cannot be empty"):
        Message(
            user_content="",  # Empty content
            created_at=datetime.now(UTC),
        )


def test_message_invalid_role_validation() -> None:
    """Test that Pydantic validation prevents invalid message roles."""
    
    from pydantic import ValidationError
    
    # Pydantic should prevent creating a message with invalid role
    with pytest.raises(ValidationError, match="Input should be 'user' or 'assistant'"):
        Message(
            user_content="Hello, how are you?",
            created_at=datetime.now(UTC),
        )


def test_validate_message_for_ai_empty_history() -> None:
    """Test validation works with empty conversation history."""
    
    message = Message(
        user_content="This is a test input with enough characters",
        system_prompt="You are a helpful AI assistant that provides accurate information.",
    )
    
    # Should not raise any exceptions
    validate_message_for_ai(message, [])


def test_validate_message_for_ai_multiple_messages() -> None:
    """Test validation works with multiple messages in history."""
    
    message1 = Message(
        user_content="Hello, how are you?",
        created_at=datetime.now(UTC),
    )
    
    message2 = Message(
        assistant_content="I'm doing well, thank you for asking!",
        created_at=datetime.now(UTC),
    )
    
    message = Message(
        user_content="This is a test input with enough characters",
        system_prompt="You are a helpful AI assistant that provides accurate information.",
    )
    
    # Should not raise any exceptions
    validate_message_for_ai(message, [message1, message2])


def test_validate_message_for_ai_no_system_prompt() -> None:
    """Test validation works without system prompt."""
    
    message = Message(
        user_content="This is a test input with enough characters",
        # No system prompt
    )
    
    # Should not raise any exceptions since system prompt is optional
    validate_message_for_ai(message)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])