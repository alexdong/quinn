"""Response data models."""

import uuid

from pydantic import BaseModel, Field, field_validator

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
    prompt_version: PROMPT_VERSION = ""

    @field_validator("content", "conversation_id", "message_id")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate string fields are not empty."""
        if not v.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)
        return v


if __name__ == "__main__":
    # Demonstrate ConversationMetrics and AgentResponse usage
    print("ConversationMetrics and AgentResponse demonstration:")

    # Create conversation metrics
    metrics = ConversationMetrics(
        total_tokens_used=1250,
        total_cost_usd=0.018,
        average_response_time_ms=850,
        message_count=4,
        model_used="claude-3.5-sonnet",
        prompt_version="240715-120000",
    )
    print("Conversation metrics:")
    print(f"  Total tokens: {metrics.total_tokens_used}")
    print(f"  Total cost: ${metrics.total_cost_usd:.3f}")
    print(f"  Avg response time: {metrics.average_response_time_ms}ms")
    print(f"  Messages: {metrics.message_count}")
    print(f"  Model: {metrics.model_used}")

    # Create agent response
    response = AgentResponse(
        content="Based on your question about neural networks, here's a comprehensive explanation...",
        conversation_id="conv-12345",
        message_id="msg-67890",
        tokens_used=324,
        cost_usd=0.0048,
        response_time_ms=1200,
        model_used="claude-3.5-sonnet",
        prompt_version="240715-120000",
    )
    print("\nAgent response:")
    print(f"  ID: {response.id[:8]}...")
    print(f"  Content preview: {response.content[:80]}...")
    print(f"  Conversation ID: {response.conversation_id}")
    print(f"  Message ID: {response.message_id}")
    print(f"  Tokens used: {response.tokens_used}")
    print(f"  Cost: ${response.cost_usd:.4f}")
    print(f"  Response time: {response.response_time_ms}ms")

    # Validation examples
    try:
        invalid_metrics = ConversationMetrics(
            total_tokens_used=-1,
            model_used="gpt-4",
            prompt_version="240715-120000",
        )
    except ValueError as e:
        print(f"\nValidation error (negative tokens): {e}")

    try:
        invalid_response = AgentResponse(
            content="",
            conversation_id="conv-123",
            message_id="msg-456",
        )
    except ValueError as e:
        print(f"Validation error (empty content): {e}")

    print("ConversationMetrics and AgentResponse demonstration completed.")
