"""Response metrics tracking."""

import time

from quinn.models import ConversationMetrics

from .cost import calculate_cost


def track_response_metrics(
    start_time: float,
    model: str,
    prompt_version: str,
    input_tokens: int,
    output_tokens: int,
) -> ConversationMetrics:
    """Extract and calculate response metrics using litellm for cost calculation."""

    assert start_time > 0, "Start time must be positive"
    assert model.strip(), "Model name cannot be empty"
    assert prompt_version.strip(), "Prompt version cannot be empty"
    assert input_tokens >= 0, "Input tokens must be non-negative"
    assert output_tokens >= 0, "Output tokens must be non-negative"

    end_time = time.time()
    response_time_ms = int((end_time - start_time) * 1000)
    total_tokens = input_tokens + output_tokens

    # Calculate cost using litellm
    cost_usd = calculate_cost(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )

    return ConversationMetrics(
        total_tokens_used=total_tokens,
        total_cost_usd=cost_usd,
        average_response_time_ms=response_time_ms,
        message_count=1,
        model_used=model,
        prompt_version=prompt_version,
    )
