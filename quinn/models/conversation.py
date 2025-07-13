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
