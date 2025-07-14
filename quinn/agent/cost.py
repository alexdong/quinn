"""Cost calculation using local pricing data."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Path to pricing data directory
PRICING_DIR = Path(__file__).parent / "pricing"


def _load_pricing_data() -> dict[str, dict[str, Any]]:
    """Load all pricing data from JSON files."""
    pricing_data = {}

    pricing_files = ["openai.json", "anthropic.json", "google.json"]

    for filename in pricing_files:
        file_path = PRICING_DIR / filename
        try:
            if file_path.exists():
                with file_path.open() as f:
                    data = json.load(f)
                    # Merge models from this provider into main pricing data
                    pricing_data.update(data.get("models", {}))
            else:
                logger.warning("Pricing file not found: %s", file_path)
        except Exception as e:
            logger.error("Failed to load pricing file %s: %s", file_path, e)

    return pricing_data


def get_model_cost_info(model: str) -> dict[str, float]:
    """Get cost information for a model using local pricing data."""
    assert model.strip(), "Model name cannot be empty"

    pricing_data = _load_pricing_data()

    if model in pricing_data:
        model_info = pricing_data[model]
        result = {
            "input_cost_per_token": model_info["input_price_per_1m_tokens"] / 1_000_000,
            "output_cost_per_token": model_info["output_price_per_1m_tokens"]
            / 1_000_000,
        }
        # Add cached input pricing if available and not null
        if "cached_input_price_per_1m_tokens" in model_info and model_info["cached_input_price_per_1m_tokens"] is not None:
            result["cached_input_cost_per_token"] = (
                model_info["cached_input_price_per_1m_tokens"] / 1_000_000
            )
        return result

    # Fallback pricing for unknown models (based on Gemini 2.0 Flash)
    logger.warning("Unknown model %s, using fallback pricing", model)
    return {
        "input_cost_per_token": 0.000000075,  # $0.075 per 1M tokens
        "output_cost_per_token": 0.0000003,  # $0.30 per 1M tokens
    }


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
) -> float:
    """Calculate total cost for API usage using local pricing data.

    Args:
        model: The model name
        input_tokens: Number of regular input tokens
        output_tokens: Number of output tokens
        cached_input_tokens: Number of cached input tokens (for models that support caching)
    """
    assert model.strip(), "Model name cannot be empty"
    assert input_tokens >= 0, "Input tokens must be non-negative"
    assert output_tokens >= 0, "Output tokens must be non-negative"
    assert cached_input_tokens >= 0, "Cached input tokens must be non-negative"

    cost_info = get_model_cost_info(model)

    # Calculate regular input cost
    input_cost = input_tokens * cost_info["input_cost_per_token"]

    # Calculate cached input cost if available
    cached_cost = 0.0
    if cached_input_tokens > 0 and "cached_input_cost_per_token" in cost_info:
        cached_cost = cached_input_tokens * cost_info["cached_input_cost_per_token"]
    elif cached_input_tokens > 0:
        # If no cached pricing available, use regular input pricing
        cached_cost = cached_input_tokens * cost_info["input_cost_per_token"]

    # Calculate output cost
    output_cost = output_tokens * cost_info["output_cost_per_token"]

    return input_cost + cached_cost + output_cost


def get_cost_per_token(model: str, token_type: str = "input") -> float:
    """Get cost per token for a specific model and token type."""
    assert model.strip(), "Model name cannot be empty"
    assert token_type in ("input", "output", "cached_input"), (
        "Token type must be 'input', 'output', or 'cached_input'"
    )

    cost_info = get_model_cost_info(model)

    if token_type == "input":
        return cost_info["input_cost_per_token"]
    if token_type == "output":
        return cost_info["output_cost_per_token"]
    # cached_input
    return cost_info.get(
        "cached_input_cost_per_token", cost_info["input_cost_per_token"]
    )


def estimate_completion_cost(
    model: str,
    prompt: str,
    max_tokens: int = 1000,
) -> dict[str, float]:
    """Estimate cost for a completion before making the API call."""
    assert model.strip(), "Model name cannot be empty"
    assert prompt.strip(), "Prompt cannot be empty"
    assert max_tokens > 0, "Max tokens must be positive"

    # Estimate input tokens (rough approximation: 4 chars per token)
    estimated_input_tokens = len(prompt) // 4

    # Use max_tokens as estimated output tokens
    estimated_output_tokens = max_tokens

    estimated_cost = calculate_cost(
        model=model,
        input_tokens=estimated_input_tokens,
        output_tokens=estimated_output_tokens,
    )

    cost_info = get_model_cost_info(model)

    return {
        "estimated_total_cost": estimated_cost,
        "estimated_input_tokens": estimated_input_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "input_cost_per_token": cost_info["input_cost_per_token"],
        "output_cost_per_token": cost_info["output_cost_per_token"],
    }


def get_supported_models() -> list[str]:
    """Get list of models with known pricing data."""
    pricing_data = _load_pricing_data()
    return list(pricing_data.keys())


if __name__ == "__main__":
    """Demonstrate cost calculation functionality."""
    print("🧮 Cost Calculation Demo")
    print("=" * 50)

    # Test models from our pricing files
    test_models = [
        "gpt-4o-mini",
        "o3",
        "o4-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "claude-3-5-sonnet-20241022",
        "claude-opus-4-20250514",
        "claude-sonnet-4",
        "claude-haiku-3.5",
        "gemini-2.0-flash",
        "gemini-2.5-flash-exp",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "unknown-model",  # Test fallback
    ]

    test_input_tokens = 1000
    test_output_tokens = 500
    test_cached_tokens = 2000

    print(
        f"📊 Testing with {test_input_tokens:,} input, {test_output_tokens:,} output, and {test_cached_tokens:,} cached tokens:\n"
    )

    for model in test_models:
        print(f"🤖 Model: {model}")

        try:
            # Get cost info
            cost_info = get_model_cost_info(model)
            print(f"   Input cost per token: ${cost_info['input_cost_per_token']:.8f}")
            print(
                f"   Output cost per token: ${cost_info['output_cost_per_token']:.8f}"
            )
            if "cached_input_cost_per_token" in cost_info:
                print(
                    f"   Cached input cost per token: ${cost_info['cached_input_cost_per_token']:.8f}"
                )

            # Calculate total cost without caching
            total_cost = calculate_cost(model, test_input_tokens, test_output_tokens)
            print(f"   Total cost (no cache): ${total_cost:.6f}")

            # Calculate total cost with caching
            total_cost_with_cache = calculate_cost(
                model, test_input_tokens, test_output_tokens, test_cached_tokens
            )
            print(f"   Total cost (with cache): ${total_cost_with_cache:.6f}")

            if total_cost_with_cache < total_cost:
                savings = total_cost - total_cost_with_cache
                savings_percent = (savings / total_cost) * 100
                print(f"   💰 Cache savings: ${savings:.6f} ({savings_percent:.1f}%)")

            # Test individual token costs
            input_cost_per_token = get_cost_per_token(model, "input")
            output_cost_per_token = get_cost_per_token(model, "output")
            cached_cost_per_token = get_cost_per_token(model, "cached_input")
            print(
                f"   Verified - Input: ${input_cost_per_token:.8f}, Output: ${output_cost_per_token:.8f}, Cached: ${cached_cost_per_token:.8f}"
            )

        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

    # Test estimation
    print("📝 Testing cost estimation:")
    test_prompt = (
        "What is the capital of France? Please provide a detailed explanation."
    )
    max_tokens = 200

    for model in test_models[:3]:  # Test first 3 models
        try:
            estimate = estimate_completion_cost(model, test_prompt, max_tokens)
            print(f"🤖 {model}:")
            print(f"   Estimated cost: ${estimate['estimated_total_cost']:.6f}")
            print(f"   Input tokens: {estimate['estimated_input_tokens']}")
            print(f"   Output tokens: {estimate['estimated_output_tokens']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()

    # Show supported models
    print("✅ Supported models:")
    supported = get_supported_models()
    for model in supported:
        print(f"   - {model}")

    print(f"\n📈 Total models with pricing data: {len(supported)}")
    print("🧮 Cost calculation demo completed!")
