"""Message data model."""

import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .response import MessageMetrics


class Message(BaseModel):
    """Single message in a conversation thread with LLM API metadata."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Literal["user", "assistant"] = "user"
    content: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Optional fields from AgentResponse
    conversation_id: str = ""

    # Prompt context
    system_prompt: str = ""

    # Individual message/API call metrics
    metadata: MessageMetrics | None = Field(default=None)

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content is not empty."""
        if not v.strip():
            msg = "Message content cannot be empty"
            raise ValueError(msg)
        return v


if __name__ == "__main__":
    # Demonstrate Message usage
    print("Message demonstration:")

    # Create user message
    user_message = Message(content="Hello, Quinn!", role="user")
    print(f"User message: {user_message.content} (ID: {user_message.id[:8]}...)")

    # Create assistant message with metrics
    assistant_message = Message(
        content="Hello! How can I help you today?",
        role="assistant",
        conversation_id="conv-12345",
        metadata=MessageMetrics(
            tokens_used=45,
            cost_usd=0.001,
            response_time_ms=800,
            model_used="claude-3.5-sonnet",
            prompt_version="240715-120000",
        ),
    )
    print(f"Assistant message: {assistant_message.content}")
    print(f"Conversation ID: {assistant_message.conversation_id}")
    print(f"Metadata: {assistant_message.metadata}")

    # Validation example
    try:
        invalid_message = Message(content="")
    except ValueError as e:
        print(f"Validation error (empty content): {e}")

    print("Message demonstration completed.")
