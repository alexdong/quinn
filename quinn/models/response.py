"""Response data models."""

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


if __name__ == "__main__":
    # Demonstrate ConversationMetrics and MessageMetrics usage
    print("ConversationMetrics and MessageMetrics demonstration:")

    # Create conversation metrics
    conv_metrics = ConversationMetrics(
        total_tokens_used=1250,
        total_cost_usd=0.018,
        average_response_time_ms=850,
        message_count=4,
        model_used="claude-3.5-sonnet",
        prompt_version="240715-120000",
    )
    print("Conversation metrics:")
    print(f"  Total tokens: {conv_metrics.total_tokens_used}")
    print(f"  Total cost: ${conv_metrics.total_cost_usd:.3f}")
    print(f"  Avg response time: {conv_metrics.average_response_time_ms}ms")
    print(f"  Messages: {conv_metrics.message_count}")
    print(f"  Model: {conv_metrics.model_used}")

    # Create message metrics
    msg_metrics = MessageMetrics(
        tokens_used=324,
        cost_usd=0.0048,
        response_time_ms=1200,
        model_used="claude-3.5-sonnet",
        prompt_version="240715-120000",
    )
    print("\nMessage metrics:")
    print(f"  Tokens used: {msg_metrics.tokens_used}")
    print(f"  Cost: ${msg_metrics.cost_usd:.4f}")
    print(f"  Response time: {msg_metrics.response_time_ms}ms")
    print(f"  Model: {msg_metrics.model_used}")

    # Validation examples
    try:
        invalid_conv_metrics = ConversationMetrics(
            total_tokens_used=-1,
            model_used="gpt-4",
            prompt_version="240715-120000",
        )
    except ValueError as e:
        print(f"\nValidation error (negative tokens): {e}")

    try:
        invalid_msg_metrics = MessageMetrics(
            model_used="",
            prompt_version="240715-120000",
        )
    except ValueError as e:
        print(f"Validation error (empty model): {e}")

    print("ConversationMetrics and MessageMetrics demonstration completed.")
