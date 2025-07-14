"""Configuration data models."""

import os
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
    api_key: str = Field(default="", min_length=0)

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
            model="claude-3-5-sonnet-20241022",
            temperature=0.6,
            max_tokens=8000,
            timeout_seconds=600,
            max_retries=3,
            retry_backoff_factor=2.0,
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        )

    @classmethod
    def flash25(cls) -> "AgentConfig":
        """Gemini 2.5 Flash configuration for fast responses."""
        return cls(
            model="gemini/gemini-2.5-flash",
            temperature=0.7,
            max_tokens=4000,
            timeout_seconds=300,
            max_retries=3,
            retry_backoff_factor=2.0,
            api_key=os.getenv("GEMINI_API_KEY", ""),
        )

    @classmethod
    def flash25thinking(cls) -> "AgentConfig":
        """Gemini 2.5 Flash configuration with thinking tokens enabled."""
        return cls(
            model="gemini/gemini-2.5-flash",
            temperature=0.7,
            max_tokens=12000,
            timeout_seconds=400,
            max_retries=3,
            retry_backoff_factor=2.0,
            model_settings={"gemini_thinking_config": {"thinking_budget": 4096}},
            api_key=os.getenv("GEMINI_API_KEY", ""),
        )

    @classmethod
    def o4mini(cls) -> "AgentConfig":
        """OpenAI GPT-4 Omni Mini configuration for efficient processing."""
        return cls(
            model="gpt-4o-mini",
            temperature=0.8,
            max_tokens=3000,
            timeout_seconds=240,
            max_retries=4,
            retry_backoff_factor=1.8,
            api_key=os.getenv("OPENAI_API_KEY", ""),
        )

    @classmethod
    def o3(cls) -> "AgentConfig":
        """OpenAI O3 configuration for advanced reasoning."""
        return cls(
            model="o3",
            temperature=0.6,
            max_tokens=8000,
            timeout_seconds=900,
            max_retries=3,
            retry_backoff_factor=2.0,
            api_key=os.getenv("OPENAI_API_KEY", ""),
        )

    @classmethod
    def o4mini_advanced(cls) -> "AgentConfig":
        """OpenAI O4-Mini configuration for cost-efficient reasoning."""
        return cls(
            model="o4-mini",
            temperature=0.7,
            max_tokens=4000,
            timeout_seconds=300,
            max_retries=3,
            retry_backoff_factor=2.0,
            api_key=os.getenv("OPENAI_API_KEY", ""),
        )

    @classmethod
    def gpt41(cls) -> "AgentConfig":
        """GPT-4.1 configuration for extended context."""
        return cls(
            model="gpt-4.1",
            temperature=0.7,
            max_tokens=8000,
            timeout_seconds=600,
            max_retries=3,
            retry_backoff_factor=2.0,
            api_key=os.getenv("OPENAI_API_KEY", ""),
        )

    @classmethod
    def gpt41mini(cls) -> "AgentConfig":
        """GPT-4.1 Mini configuration for balanced performance."""
        return cls(
            model="gpt-4.1-mini",
            temperature=0.7,
            max_tokens=4000,
            timeout_seconds=300,
            max_retries=3,
            retry_backoff_factor=2.0,
            api_key=os.getenv("OPENAI_API_KEY", ""),
        )

    @classmethod
    def gpt41nano(cls) -> "AgentConfig":
        """GPT-4.1 Nano configuration for ultra-efficient processing."""
        return cls(
            model="gpt-4.1-nano",
            temperature=0.8,
            max_tokens=2000,
            timeout_seconds=180,
            max_retries=4,
            retry_backoff_factor=1.5,
            api_key=os.getenv("OPENAI_API_KEY", ""),
        )

    @classmethod
    def opus4(cls) -> "AgentConfig":
        """Claude Opus 4 configuration for most complex tasks."""
        return cls(
            model="claude-opus-4-20250514",
            temperature=0.5,
            max_tokens=8000,
            timeout_seconds=900,
            max_retries=3,
            retry_backoff_factor=2.5,
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        )

    @classmethod
    def sonnet4_new(cls) -> "AgentConfig":
        """Claude Sonnet 4 configuration for balanced reasoning."""
        return cls(
            model="claude-sonnet-4",
            temperature=0.6,
            max_tokens=6000,
            timeout_seconds=600,
            max_retries=3,
            retry_backoff_factor=2.0,
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        )

    @classmethod
    def haiku35(cls) -> "AgentConfig":
        """Claude Haiku 3.5 configuration for fast responses."""
        return cls(
            model="claude-haiku-3.5",
            temperature=0.8,
            max_tokens=3000,
            timeout_seconds=180,
            max_retries=4,
            retry_backoff_factor=1.5,
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        )

    @classmethod
    def gemini20flash(cls) -> "AgentConfig":
        """Gemini 2.0 Flash configuration for general use."""
        return cls(
            model="gemini-2.0-flash",
            temperature=0.7,
            max_tokens=4000,
            timeout_seconds=300,
            max_retries=3,
            retry_backoff_factor=2.0,
            api_key=os.getenv("GEMINI_API_KEY", ""),
        )

    @classmethod
    def gemini25pro(cls) -> "AgentConfig":
        """Gemini 2.5 Pro configuration for complex tasks."""
        return cls(
            model="gemini-2.5-pro",
            temperature=0.6,
            max_tokens=8000,
            timeout_seconds=600,
            max_retries=3,
            retry_backoff_factor=2.0,
            api_key=os.getenv("GEMINI_API_KEY", ""),
        )

    @classmethod
    def gemini25flash(cls) -> "AgentConfig":
        """Gemini 2.5 Flash configuration for best price/performance."""
        return cls(
            model="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=4000,
            timeout_seconds=300,
            max_retries=3,
            retry_backoff_factor=2.0,
            api_key=os.getenv("GEMINI_API_KEY", ""),
        )


if __name__ == "__main__":
    # Demonstrate AgentConfig usage
    print("AgentConfig demonstration:")

    # Default configuration
    default_config = AgentConfig()
    print(f"Default config: {default_config}")

    # Prebuilt configurations
    print("\nPrebuilt configurations:")

    # OpenAI models
    print("\n🤖 OpenAI Models:")
    print(f"O4 Mini: {AgentConfig.o4mini()}")
    print(f"O3: {AgentConfig.o3()}")
    print(f"O4-Mini Advanced: {AgentConfig.o4mini_advanced()}")
    print(f"GPT-4.1: {AgentConfig.gpt41()}")
    print(f"GPT-4.1 Mini: {AgentConfig.gpt41mini()}")
    print(f"GPT-4.1 Nano: {AgentConfig.gpt41nano()}")

    # Anthropic models
    print("\n🧠 Anthropic Models:")
    print(f"Sonnet 4: {AgentConfig.sonnet4()}")
    print(f"Opus 4: {AgentConfig.opus4()}")
    print(f"Sonnet 4 (new): {AgentConfig.sonnet4_new()}")
    print(f"Haiku 3.5: {AgentConfig.haiku35()}")

    # Google models
    print("\n🚀 Google Models:")
    print(f"Flash 2.5: {AgentConfig.flash25()}")
    print(f"Flash 2.5 Thinking: {AgentConfig.flash25thinking()}")
    print(f"Gemini 2.0 Flash: {AgentConfig.gemini20flash()}")
    print(f"Gemini 2.5 Pro: {AgentConfig.gemini25pro()}")
    print(f"Gemini 2.5 Flash: {AgentConfig.gemini25flash()}")

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
