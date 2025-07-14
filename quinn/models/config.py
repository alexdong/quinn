"""Configuration data models."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class AgentConfig(BaseModel):
    """Configuration for AI agent behavior."""

    model: str = "gemini/gemini-2.5-flash-exp"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, gt=0)
    timeout_seconds: int = Field(default=300, gt=0)
    max_retries: int = Field(default=3, ge=0)
    retry_backoff_factor: float = Field(default=2.0, gt=1.0)
    model_settings: dict[str, Any] | None = Field(default=None)

    @field_validator("model")
    @classmethod
    def validate_model_not_empty(cls, v: str) -> str:
        """Validate model name is not empty."""
        if not v.strip():
            msg = "Model name cannot be empty"
            raise ValueError(msg)
        return v

    @classmethod
    def sonnet4(cls) -> "AgentConfig":
        """Claude 4 Sonnet configuration optimized for complex reasoning."""
        return cls(
            model="claude-4-sonnet-20241022",
            temperature=0.6,
            max_tokens=8000,
            timeout_seconds=600,
            max_retries=3,
            retry_backoff_factor=2.0,
        )

    @classmethod
    def flash25(cls) -> "AgentConfig":
        """Gemini 2.5 Flash configuration for fast responses."""
        return cls(
            model="gemini/gemini-2.5-flash-exp",
            temperature=0.7,
            max_tokens=4000,
            timeout_seconds=300,
            max_retries=3,
            retry_backoff_factor=2.0,
        )

    @classmethod
    def o4mini(cls) -> "AgentConfig":
        """OpenAI GPT-4 Omni Mini configuration for efficient processing."""
        return cls(
            model="openai/gpt-4o-mini",
            temperature=0.8,
            max_tokens=3000,
            timeout_seconds=240,
            max_retries=4,
            retry_backoff_factor=1.8,
        )

    @classmethod
    def flash25thinking(cls) -> "AgentConfig":
        """Gemini 2.5 Flash configuration with thinking tokens enabled."""
        return cls(
            model="gemini/gemini-2.5-flash-exp",
            temperature=0.7,
            max_tokens=6000,
            timeout_seconds=400,
            max_retries=3,
            retry_backoff_factor=2.0,
            model_settings={"gemini_thinking_config": {"thinking_budget": 4096}},
        )


if __name__ == "__main__":
    # Demonstrate AgentConfig usage
    print("AgentConfig demonstration:")

    # Default configuration
    default_config = AgentConfig()
    print(f"Default config: {default_config}")

    # Prebuilt configurations
    print("\nPrebuilt configurations:")

    sonnet_config = AgentConfig.sonnet4()
    print(f"Sonnet 4: {sonnet_config}")

    flash_config = AgentConfig.flash25()
    print(f"Flash 2.5: {flash_config}")

    flash_thinking_config = AgentConfig.flash25thinking()
    print(f"Flash 2.5 Thinking: {flash_thinking_config}")

    o4mini_config = AgentConfig.o4mini()
    print(f"O4 Mini: {o4mini_config}")

    # Custom configuration
    custom_config = AgentConfig(
        model="claude-3.5-sonnet",
        temperature=0.5,
        max_tokens=2000,
        timeout_seconds=600,
        max_retries=5,
        retry_backoff_factor=1.5,
    )
    print(f"\nCustom config: {custom_config}")

    # Validation examples
    try:
        invalid_config = AgentConfig(temperature=-0.1)
    except ValueError as e:
        print(f"\nValidation error (temperature): {e}")

    try:
        invalid_config = AgentConfig(model="")
    except ValueError as e:
        print(f"Validation error (empty model): {e}")

    print("AgentConfig demonstration completed.")
