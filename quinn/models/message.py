"""Message data model."""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator

from .response import MessageMetrics


class Message(BaseModel):
    """Single interaction containing user input and assistant response."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_content: str = ""
    assistant_content: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Conversation context
    conversation_id: str = ""
    system_prompt: str = ""

    # Assistant response metrics
    metadata: MessageMetrics | None = Field(default=None)

    @field_validator("user_content")
    @classmethod
    def validate_user_content(cls, v: str) -> str:
        """Validate user content is not empty."""
        if not v.strip():
            msg = "User content cannot be empty"
            raise ValueError(msg)
        return v


if __name__ == "__main__":
    # Demonstrate Message usage
    print("Message demonstration:")

    # Create interaction with user input only
    user_interaction = Message(user_content="Hello, Quinn!")
    print(
        f"User input: {user_interaction.user_content} (ID: {user_interaction.id[:8]}...)"
    )

    # Create complete interaction with response and metrics
    complete_interaction = Message(
        user_content="What is artificial intelligence?",
        assistant_content="AI is the simulation of human intelligence in machines...",
        conversation_id="conv-12345",
        system_prompt="You are a helpful AI assistant",
        metadata=MessageMetrics(
            tokens_used=75,
            cost_usd=0.002,
            response_time_ms=1200,
            model_used="claude-3.5-sonnet",
            prompt_version="240715-120000",
        ),
    )
    print("Complete interaction:")
    print(f"  User: {complete_interaction.user_content}")
    print(f"  Assistant: {complete_interaction.assistant_content[:50]}...")
    print(f"  Conversation ID: {complete_interaction.conversation_id}")
    print(f"  Metadata: {complete_interaction.metadata}")

    # Validation example
    try:
        invalid_message = Message(user_content="")
    except ValueError as e:
        print(f"Validation error (empty user content): {e}")

    print("Message demonstration completed.")
