"""Cost calculation using litellm."""

import logging

import litellm

logger = logging.getLogger(__name__)


def get_model_cost_info(model: str) -> dict[str, float]:
    """Get cost information for a model using litellm."""
    assert model.strip(), "Model name cannot be empty"

    try:
        # Use cost_per_token to get the costs for 1 token each
        input_cost, output_cost = litellm.cost_per_token(
            model=model,
            prompt_tokens=1,
            completion_tokens=1,
        )

        return {
            "input_cost_per_token": input_cost,
            "output_cost_per_token": output_cost,
        }

    except Exception as e:
        logger.error("Failed to get cost info for model %s: %s", model, e)
        # Fallback costs for Gemini 2.5 Flash
        return {
            "input_cost_per_token": 0.00000015,  # $0.15 per 1M tokens
            "output_cost_per_token": 0.0000006,  # $0.60 per 1M tokens
        }


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Calculate total cost for API usage using litellm."""
    assert model.strip(), "Model name cannot be empty"
    assert input_tokens >= 0, "Input tokens must be non-negative"
    assert output_tokens >= 0, "Output tokens must be non-negative"

    try:
        # Use litellm's cost_per_token to calculate costs
        input_cost, output_cost = litellm.cost_per_token(
            model=model,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
        )

        return input_cost + output_cost

    except Exception as e:
        logger.error("Failed to calculate cost for model %s: %s", model, e)

        # Fallback calculation
        cost_info = get_model_cost_info(model)
        input_cost = input_tokens * cost_info["input_cost_per_token"]
        output_cost = output_tokens * cost_info["output_cost_per_token"]

        return input_cost + output_cost


def get_cost_per_token(model: str, token_type: str = "input") -> float:
    """Get cost per token for a specific model and token type."""
    assert model.strip(), "Model name cannot be empty"
    assert token_type in ("input", "output"), "Token type must be 'input' or 'output'"

    cost_info = get_model_cost_info(model)

    if token_type == "input":
        return cost_info["input_cost_per_token"]
    return cost_info["output_cost_per_token"]


def estimate_completion_cost(
    model: str,
    prompt: str,
    max_tokens: int = 1000,
) -> dict[str, float]:
    """Estimate cost for a completion before making the API call."""
    assert model.strip(), "Model name cannot be empty"
    assert prompt.strip(), "Prompt cannot be empty"
    assert max_tokens > 0, "Max tokens must be positive"

    try:
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

    except Exception as e:
        logger.error("Failed to estimate cost for model %s: %s", model, e)
        return {
            "estimated_total_cost": 0.0,
            "estimated_input_tokens": 0,
            "estimated_output_tokens": 0,
            "input_cost_per_token": 0.0,
            "output_cost_per_token": 0.0,
        }
