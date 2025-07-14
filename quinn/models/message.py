"""Message data model."""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator

from .types import PROMPT_VERSION


class MessageMetrics(BaseModel):
    """Tracking metrics for individual message/LLM API calls."""

    tokens_used: int = Field(default=0, ge=0)
    cost_usd: float = Field(default=0.0, ge=0.0)
    response_time_ms: int = Field(default=0, ge=0)
    model_used: str = ""
    prompt_version: PROMPT_VERSION = ""

    @field_validator("model_used")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate string fields are not empty."""
        if not v.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)
        return v


class Message(BaseModel):
    """Single message in a conversation."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Message content
    system_prompt: str = ""
    user_content: str = ""
    assistant_content: str = ""

    @field_validator("user_content")
    @classmethod
    def validate_user_content(cls, v: str) -> str:
        """Validate user content is not empty when provided."""
        if v is not None and v.strip() == "":
            raise ValueError("Message content cannot be empty")
        return v

    # Assistant response metrics
    metadata: MessageMetrics | None = Field(default=None)


if __name__ == "__main__":
    # Demonstrate Message usage
    print("Message demonstration:")

    # Create user message
    user_message = Message(
        conversation_id="conv-12345",
        user_content="Hello, Quinn!",
        system_prompt="You are a helpful AI assistant",
    )
    print(f"User message: {user_message.user_content} (ID: {user_message.id[:8]}...)")
    print(f"Created at: {user_message.created_at}")

    # Create assistant message with metrics
    import time

    time.sleep(0.1)  # Simulate processing time

    assistant_message = Message(
        conversation_id="conv-12345",
        user_content="What is AI?",
        assistant_content="AI is the simulation of human intelligence in machines...",
        system_prompt="You are a helpful AI assistant",
        last_updated_at=datetime.now(UTC),  # Simulate response received
        metadata=MessageMetrics(
            tokens_used=75,
            cost_usd=0.002,
            response_time_ms=1200,
            model_used="claude-3.5-sonnet",
            prompt_version="240715-120000",
        ),
    )
    print("Assistant message:")
    print(f"  User content: {assistant_message.user_content}")
    print(f"  Assistant content: {assistant_message.assistant_content[:50]}...")
    print(f"  Created: {assistant_message.created_at}")
    print(f"  Updated: {assistant_message.last_updated_at}")
    print(f"  Conversation ID: {assistant_message.conversation_id}")
    print(f"  Metadata: {assistant_message.metadata}")

    print("Message demonstration completed.")
