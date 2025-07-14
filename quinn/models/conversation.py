"""Conversation data models."""

import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from .message import Message
from .response import ConversationMetrics


class Conversation(BaseModel):
    """A conversation containing multiple messages."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metrics: ConversationMetrics | None = Field(default=None)

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation and update metrics."""
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)
        self._update_metrics()

    def _update_metrics(self) -> None:
        """Update conversation metrics based on current messages."""
        if not self.messages:
            self.metrics = None
            return

        # Calculate aggregated metrics from all messages with metadata
        messages_with_metrics = [
            msg for msg in self.messages if msg.metadata is not None
        ]

        if not messages_with_metrics:
            self.metrics = None
            return

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

        # Use the latest message's model and prompt version as representative
        latest_with_metrics = messages_with_metrics[-1]

        self.metrics = ConversationMetrics(
            total_tokens_used=total_tokens,
            total_cost_usd=total_cost,
            average_response_time_ms=avg_response_time,
            message_count=len(self.messages),
            model_used=latest_with_metrics.metadata.model_used,
            prompt_version=latest_with_metrics.metadata.prompt_version,
        )

    def get_latest_message(self) -> Message | None:
        """Get the most recent message."""
        return self.messages[-1] if self.messages else None

    def get_messages_by_role(self, role: Literal["user", "assistant"]) -> list[Message]:
        """Get all messages by role."""
        return [msg for msg in self.messages if msg.role == role]


if __name__ == "__main__":
    # Demonstrate Message and Conversation usage
    print("Message and Conversation demonstration:")

    from .response import MessageMetrics

    # Create messages
    user_message = Message(content="Hello, Quinn!", role="user")
    print(f"User message: {user_message.content} (ID: {user_message.id[:8]}...)")

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
    print(f"Metadata: {assistant_message.metadata}")

    # Create conversation
    conversation = Conversation()
    print(f"\nNew conversation created (ID: {conversation.id[:8]}...)")
    print(f"Created at: {conversation.created_at}")

    # Add messages
    conversation.add_message(user_message)
    conversation.add_message(assistant_message)
    print(f"Added 2 messages, conversation updated at: {conversation.updated_at}")
    print(f"Conversation metrics: {conversation.metrics}")

    # Query conversation
    latest_message = conversation.get_latest_message()
    print(f"Latest message: {latest_message.content if latest_message else 'None'}")

    user_messages = conversation.get_messages_by_role("user")
    assistant_messages = conversation.get_messages_by_role("assistant")
    print(f"User messages: {len(user_messages)}")
    print(f"Assistant messages: {len(assistant_messages)}")

    # Create another assistant message to test metric aggregation
    second_assistant_message = Message(
        content="I can help with various tasks.",
        role="assistant",
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

    # Validation example
    try:
        invalid_message = Message(content="")
    except ValueError as e:
        print(f"Validation error (empty content): {e}")

    print("Message and Conversation demonstration completed.")
