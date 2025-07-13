"""Prompt context validation."""

from quinn.models import PromptContext

# Validation constants
MIN_USER_INPUT_LENGTH = 10
MIN_SYSTEM_PROMPT_LENGTH = 50


def validate_prompt_context(context: PromptContext) -> None:
    """Validate prompt context before sending to AI."""
    assert isinstance(context, PromptContext), "Context must be PromptContext instance"

    # Additional validation beyond dataclass __post_init__
    assert len(context.user_input.strip()) >= MIN_USER_INPUT_LENGTH, (
        "User input too short (min 10 chars)"
    )
    assert len(context.system_prompt.strip()) >= MIN_SYSTEM_PROMPT_LENGTH, (
        "System prompt too short (min 50 chars)"
    )

    # Validate conversation history if present
    for i, message in enumerate(context.conversation_history):
        assert message.content.strip(), f"Empty message content at index {i}"
        assert message.role in ("user", "assistant"), (
            f"Invalid role at index {i}: {message.role}"
        )
