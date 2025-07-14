"""Message validation for AI processing."""

from quinn.models import Message

# Validation constants
MIN_USER_INPUT_LENGTH = 10
MIN_SYSTEM_PROMPT_LENGTH = 50


def validate_message_for_ai(
    message: Message, conversation_history: list[Message] | None = None
) -> None:
    """Validate message before sending to AI."""
    assert isinstance(message, Message), "Message must be Message instance"

    # Additional validation beyond model validation
    assert len(message.user_content.strip()) >= MIN_USER_INPUT_LENGTH, (
        "User content too short (min 10 chars)"
    )

    # Only validate system prompt if it's provided
    if message.system_prompt.strip():
        assert len(message.system_prompt.strip()) >= MIN_SYSTEM_PROMPT_LENGTH, (
            "System prompt too short (min 50 chars)"
        )

    # Validate conversation history if present
    if conversation_history:
        for i, hist_message in enumerate(conversation_history):
            assert hist_message.user_content.strip(), f"Empty user content at index {i}"
