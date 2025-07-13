"""Response data models."""

import uuid

from pydantic import BaseModel, Field, field_validator


class ConversationMetrics(BaseModel):
    """Tracking metrics for conversations and responses."""

    total_tokens_used: int = Field(default=0, ge=0)
    total_cost_usd: float = Field(default=0.0, ge=0.0)
    average_response_time_ms: int = Field(default=0, ge=0)
    message_count: int = Field(default=0, ge=0)
    model_used: str = ""
    prompt_version: str = ""

    @field_validator("model_used", "prompt_version")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate string fields are not empty."""
        if not v.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)
        return v


class AgentResponse(BaseModel):
    """Complete response from AI agent with metadata."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    conversation_id: str = ""
    message_id: str = ""

    # Individual response metrics
    tokens_used: int = Field(default=0, ge=0)
    cost_usd: float = Field(default=0.0, ge=0.0)
    response_time_ms: int = Field(default=0, ge=0)
    model_used: str = ""
    prompt_version: str = ""

    @field_validator("content", "conversation_id", "message_id")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate string fields are not empty."""
        if not v.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)
        return v
