"""Configuration data models."""

from pydantic import BaseModel, Field, field_validator


class AgentConfig(BaseModel):
    """Configuration for AI agent behavior."""

    model: str = "gemini-2.5-flash-exp"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, gt=0)
    timeout_seconds: int = Field(default=300, gt=0)
    max_retries: int = Field(default=3, ge=0)
    retry_backoff_factor: float = Field(default=2.0, gt=1.0)
    input_cost_per_token: float = Field(
        default=0.00000015, ge=0.0,
    )  # $0.15 per 1M tokens
    output_cost_per_token: float = Field(
        default=0.0000006, ge=0.0,
    )  # $0.60 per 1M tokens

    @field_validator("model")
    @classmethod
    def validate_model_not_empty(cls, v: str) -> str:
        """Validate model name is not empty."""
        if not v.strip():
            msg = "Model name cannot be empty"
            raise ValueError(msg)
        return v
