"""Conversation data models."""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator

from .message import Message
from .types import PROMPT_VERSION


class ConversationMetrics(BaseModel):
    """Tracking metrics for conversations and responses."""

    total_tokens_used: int = Field(default=0, ge=0)
    total_cost_usd: float = Field(default=0.0, ge=0.0)
    average_response_time_ms: int = Field(default=0, ge=0)
    message_count: int = Field(default=0, ge=0)
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


class Conversation(BaseModel):
    """A conversation containing multiple messages."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def metrics(self) -> ConversationMetrics | None:
        """Calculate conversation metrics based on current messages."""
        if not self.messages:
            return None

        messages_with_metrics = [
            msg for msg in self.messages if msg.metadata is not None
        ]

        if not messages_with_metrics:
            return None

        total_tokens = sum(msg.metadata.tokens_used for msg in messages_with_metrics)
        total_cost = sum(msg.metadata.cost_usd for msg in messages_with_metrics)
        response_times = [
            msg.metadata.response_time_ms
            for msg in messages_with_metrics
            if msg.metadata.response_time_ms > 0
        ]
        avg_response_time = (
            int(sum(response_times) / len(response_times)) if response_times else 0
        )

        latest_with_metrics = messages_with_metrics[-1]

        return ConversationMetrics(
            total_tokens_used=total_tokens,
            total_cost_usd=total_cost,
            average_response_time_ms=avg_response_time,
            message_count=len(self.messages),
            model_used=latest_with_metrics.metadata.model_used,
            prompt_version=latest_with_metrics.metadata.prompt_version,
        )

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

    def get_latest_message(self) -> Message | None:
        """Get the most recent message."""
        return self.messages[-1] if self.messages else None


if __name__ == "__main__":
    import sys
    # Only run demonstration if not in test environment
    if "pytest" not in sys.modules:
        # Demonstrate Message and Conversation usage
        print("Message and Conversation demonstration:")

        from .message import MessageMetrics

        message = Message(
            user_content="Hello! How can I help you today?",
            conversation_id="conv-12345",
            metadata=MessageMetrics(
                tokens_used=45,
                cost_usd=0.001,
                response_time_ms=800,
                model_used="claude-3.5-sonnet",
                prompt_version="240715-120000",
            ),
        )
        print(f"Assistant message: {message.user_content}")
        print(f"Metadata: {message.metadata}")

        # Create conversation
        conversation = Conversation()
        print(f"\nNew conversation created (ID: {conversation.id[:8]}...)")
        print(f"Created at: {conversation.created_at}")

        # Add messages
        conversation.add_message(message)
        print(f"Added 2 messages, conversation updated at: {conversation.updated_at}")
        print(f"Conversation metrics: {conversation.metrics}")

        # Query conversation
        latest_message = conversation.get_latest_message()
        print(
            f"Latest message: {latest_message.user_content if latest_message else 'None'}"
        )

        # Create another assistant message to test metric aggregation
        second_assistant_message = Message(
            user_content="I can help with various tasks.",
            conversation_id="conv-12345",
            metadata=MessageMetrics(
                tokens_used=30,
                cost_usd=0.0008,
                response_time_ms=600,
                model_used="claude-3.5-sonnet",
                prompt_version="240715-120000",
            ),
        )
        conversation.add_message(second_assistant_message)
        print(f"After adding 3rd message, metrics: {conversation.metrics}")

        print("Message and Conversation demonstration completed.")
