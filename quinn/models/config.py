"""Configuration data models."""

import inspect
import os
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AgentConfig(BaseModel):
    """Configuration for AI agent behavior."""

    model: str = "gemini-2.5-flash-exp"
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
    def sonnet4(cls) -> "AgentConfig":
        """Claude Sonnet 4 configuration for balanced reasoning."""
        return cls(
            model="claude-sonnet-4-20250514",
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

    @classmethod
    def gemini25flashthinking(cls) -> "AgentConfig":
        """Gemini 2.5 Flash configuration with thinking tokens enabled."""
        return cls(
            model="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=12000,
            timeout_seconds=400,
            max_retries=3,
            retry_backoff_factor=2.0,
            model_settings={"gemini_thinking_config": {"thinking_budget": 4096}},
            api_key=os.getenv("GEMINI_API_KEY", ""),
        )

    @classmethod
    def get_all_models(cls) -> list[str]:
        """Get all available model names from class methods."""

        models = []
        # Get all class methods that return AgentConfig instances
        for name, method in inspect.getmembers(cls, predicate=inspect.ismethod):
            # Skip private methods and the current method
            if name.startswith("_") or name == "get_all_models":
                continue

            # Check if it's a classmethod that returns AgentConfig
            if hasattr(method, "__self__") and method.__self__ is cls:
                sig = inspect.signature(method)
                # Skip methods that expect additional arguments
                if len(sig.parameters) > 0:
                    continue

                config_instance = method()
                assert isinstance(config_instance, cls), (
                    f"Method {name} did not return an AgentConfig instance"
                )
                models.append(config_instance.model)

        return list(set(models))


def main() -> None:
    """Demonstrate AgentConfig functionality."""
    print("AgentConfig demonstration:")

    default_config = AgentConfig()
    print(f"Default config: {default_config}")

    print("\nAvailable models:")
    models = AgentConfig.get_all_models()
    for model in models:
        print(f"  - {model}")

    print(f"\nTotal models available: {len(models)}")


if __name__ == "__main__":
    main()
