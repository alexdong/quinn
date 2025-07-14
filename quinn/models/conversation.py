"""Conversation data models."""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from .response import ConversationMetrics


class Message(BaseModel):
    """Single message in a conversation thread."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Literal["user", "assistant"] = "user"
    content: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content is not empty."""
        if not v.strip():
            msg = "Message content cannot be empty"
            raise ValueError(msg)
        return v


class Conversation(BaseModel):
    """A conversation containing multiple messages."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metrics: "ConversationMetrics | None" = Field(default=None)

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

    def get_latest_message(self) -> Message | None:
        """Get the most recent message."""
        return self.messages[-1] if self.messages else None

    def get_messages_by_role(self, role: Literal["user", "assistant"]) -> list[Message]:
        """Get all messages by role."""
        return [msg for msg in self.messages if msg.role == role]


if __name__ == "__main__":
    # Demonstrate Message and Conversation usage
    print("Message and Conversation demonstration:")

    # Create messages
    user_message = Message(content="Hello, Quinn!", role="user")
    print(f"User message: {user_message.content} (ID: {user_message.id[:8]}...)")

    assistant_message = Message(
        content="Hello! How can I help you today?",
        role="assistant",
        metadata={"model": "claude-3.5-sonnet", "tokens": 45},
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

    # Query conversation
    latest_message = conversation.get_latest_message()
    print(f"Latest message: {latest_message.content if latest_message else 'None'}")

    user_messages = conversation.get_messages_by_role("user")
    assistant_messages = conversation.get_messages_by_role("assistant")
    print(f"User messages: {len(user_messages)}")
    print(f"Assistant messages: {len(assistant_messages)}")

    # Validation example
    try:
        invalid_message = Message(content="")
    except ValueError as e:
        print(f"Validation error (empty content): {e}")

    print("Message and Conversation demonstration completed.")
