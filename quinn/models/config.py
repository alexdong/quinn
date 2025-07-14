"""Configuration data models."""

from pydantic import BaseModel, Field, field_validator


class AgentConfig(BaseModel):
    """Configuration for AI agent behavior."""

    model: str = "gemini/gemini-2.5-flash-exp"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, gt=0)
    timeout_seconds: int = Field(default=300, gt=0)
    max_retries: int = Field(default=3, ge=0)
    retry_backoff_factor: float = Field(default=2.0, gt=1.0)

    @field_validator("model")
    @classmethod
    def validate_model_not_empty(cls, v: str) -> str:
        """Validate model name is not empty."""
        if not v.strip():
            msg = "Model name cannot be empty"
            raise ValueError(msg)
        return v


if __name__ == "__main__":
    # Demonstrate AgentConfig usage
    print("AgentConfig demonstration:")
    
    # Default configuration
    default_config = AgentConfig()
    print(f"Default config: {default_config}")
    
    # Custom configuration
    custom_config = AgentConfig(
        model="claude-3.5-sonnet",
        temperature=0.5,
        max_tokens=2000,
        timeout_seconds=600,
        max_retries=5,
        retry_backoff_factor=1.5,
    )
    print(f"Custom config: {custom_config}")
    
    # Validation examples
    try:
        invalid_config = AgentConfig(temperature=-0.1)
    except ValueError as e:
        print(f"Validation error (temperature): {e}")
    
    try:
        invalid_config = AgentConfig(model="")
    except ValueError as e:
        print(f"Validation error (empty model): {e}")
    
    print("AgentConfig demonstration completed.")
