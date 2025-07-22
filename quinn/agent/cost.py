"""Cost calculation using local pricing data."""

import json
import logging
from pathlib import Path
from typing import Any, NamedTuple

logger = logging.getLogger(__name__)

# Path to pricing data directory
PRICING_DIR = Path(__file__).parent / "pricing"


def _load_pricing_data() -> dict[str, dict[str, Any]]:
    """Load all pricing data from JSON files."""
    pricing_data = {}

    pricing_files = [f.name for f in PRICING_DIR.glob("*.json")]
    for filename in pricing_files:
        file_path = PRICING_DIR / filename
        assert file_path.exists(), f"Pricing file {filename} does not exist"
        with file_path.open() as f:
            data = json.load(f).get("models", {})
            assert data, f"No valid pricing data found in {filename}"

            # Ensure we only load the key-value pairs with `_price_` in their keys
            data = {
                k: v
                for k, v in data.items()
                if isinstance(v, dict) and any("_price_" in key for key in v)
            }
            pricing_data.update(data)

    return pricing_data


MODEL_PRICING: dict[str, dict[str, float]] = _load_pricing_data()


class ModelCostInfo(NamedTuple):
    """Structured cost information for a model."""

    input_cost_per_token: float
    output_cost_per_token: float
    cached_input_cost_per_token: float | None


def get_model_cost_info(model: str) -> ModelCostInfo:
    """Get cost information for a model using local pricing data."""
    assert model.strip(), "Model name cannot be empty"
    assert model in MODEL_PRICING, f"Model {model} not found in pricing data"

    model_info = MODEL_PRICING[model]
    assert "cached_input_price_per_1m_tokens" in model_info, (
        f"Model {model} does not have cached input pricing data"
    )

    # Handle cached pricing (may be None for some models)
    cached_price = model_info["cached_input_price_per_1m_tokens"]
    cached_cost_per_token = (
        cached_price / 1_000_000 if cached_price is not None else None
    )

    return ModelCostInfo(
        input_cost_per_token=model_info["input_price_per_1m_tokens"] / 1_000_000,
        output_cost_per_token=model_info["output_price_per_1m_tokens"] / 1_000_000,
        cached_input_cost_per_token=cached_cost_per_token,
    )


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
    input_cost = input_tokens * cost_info.input_cost_per_token

    # Calculate cached input cost if available
    cached_cost = 0.0
    if cached_input_tokens > 0:
        cached_cost_per_token = cost_info.cached_input_cost_per_token
        if cached_cost_per_token is not None:
            cached_cost = cached_input_tokens * cached_cost_per_token
        else:
            # If no cached pricing available, use regular input pricing
            cached_cost = cached_input_tokens * cost_info.input_cost_per_token

    # Calculate output cost
    output_cost = output_tokens * cost_info.output_cost_per_token

    return input_cost + cached_cost + output_cost


def get_cost_per_token(model: str, token_type: str = "input") -> float:
    """Get cost per token for a specific model and token type."""
    assert model.strip(), "Model name cannot be empty"
    assert token_type in (
        "input",
        "output",
        "cached_input",
    ), "Token type must be 'input', 'output', or 'cached_input'"

    cost_info = get_model_cost_info(model)

    if token_type == "input":
        return cost_info.input_cost_per_token
    if token_type == "output":
        return cost_info.output_cost_per_token
    # cached_input
    cached_cost = cost_info.cached_input_cost_per_token
    return cached_cost if cached_cost is not None else cost_info.input_cost_per_token


class CompletionCostEstimate(NamedTuple):
    """Estimated cost information for a completion."""

    estimated_total_cost: float
    estimated_input_tokens: int
    estimated_output_tokens: int
    input_cost_per_token: float
    output_cost_per_token: float


def estimate_completion_cost(
    model: str,
    prompt: str,
    max_tokens: int = 1000,
) -> CompletionCostEstimate:
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

    return CompletionCostEstimate(
        estimated_total_cost=estimated_cost,
        estimated_input_tokens=estimated_input_tokens,
        estimated_output_tokens=estimated_output_tokens,
        input_cost_per_token=cost_info.input_cost_per_token,
        output_cost_per_token=cost_info.output_cost_per_token,
    )


def get_supported_models() -> list[str]:
    """Get list of models with known pricing data."""
    return list(MODEL_PRICING.keys())


def _demo_model_costs(
    model: str, input_tokens: int, output_tokens: int, cached_tokens: int
) -> None:
    """Demo cost calculations for a single model."""
    print(f"🤖 Model: {model}")

    # Get cost info
    cost_info = get_model_cost_info(model)
    print(f"   Input cost per token: ${cost_info.input_cost_per_token:.8f}")
    print(f"   Output cost per token: ${cost_info.output_cost_per_token:.8f}")
    cached_cost = cost_info.cached_input_cost_per_token
    if cached_cost is not None:
        print(f"   Cached input cost per token: ${cached_cost:.8f}")
    else:
        print("   Cached input cost per token: Not supported")

    # Calculate total cost without caching
    total_cost = calculate_cost(model, input_tokens, output_tokens)
    print(f"   Total cost (no cache): ${total_cost:.6f}")

    # Calculate total cost with caching
    total_cost_with_cache = calculate_cost(
        model, input_tokens, output_tokens, cached_tokens
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
    print()


def _demo_cost_estimation(models: list[str]) -> None:
    """Demo cost estimation for sample models."""
    print("📝 Testing cost estimation:")
    test_prompt = (
        "What is the capital of France? Please provide a detailed explanation."
    )
    max_tokens = 200

    for model in models[:3]:  # Test first 3 models
        try:
            estimate = estimate_completion_cost(model, test_prompt, max_tokens)
            print(f"🤖 {model}:")
            print(f"   Estimated cost: ${estimate.estimated_total_cost:.6f}")
            print(f"   Input tokens: {estimate.estimated_input_tokens}")
            print(f"   Output tokens: {estimate.estimated_output_tokens}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()


def main() -> None:
    """Demonstrate cost calculation functionality."""
    print("🧮 Cost Calculation Demo")
    print("=" * 50)

    # Test models from our pricing files
    test_models = get_supported_models()
    test_input_tokens = 1000
    test_output_tokens = 500
    test_cached_tokens = 2000
    print(
        f"📊 Testing with {test_input_tokens:,} input, {test_output_tokens:,} output, and {test_cached_tokens:,} cached tokens:\n"
    )

    # Demo cost calculations for each model
    for model in test_models:
        _demo_model_costs(
            model, test_input_tokens, test_output_tokens, test_cached_tokens
        )

    # Demo cost estimation
    _demo_cost_estimation(test_models)

    # Show supported models
    print("✅ Supported models:")
    for model in test_models:
        print(f"   - {model}")

    print(f"\n📈 Total models with pricing data: {len(test_models)}")
    print("🧮 Cost calculation demo completed!")


if __name__ == "__main__":
    main()
