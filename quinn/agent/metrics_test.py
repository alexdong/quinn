"""Test response metrics tracking."""

import time

import pytest

from .metrics import track_response_metrics


def test_track_response_metrics() -> None:
    """Test response metrics tracking."""
    start_time = time.time()
    
    # Wait a tiny bit to ensure response time > 0
    time.sleep(0.001)
    
    metrics = track_response_metrics(
        start_time=start_time,
        model="gemini-2.5-flash-exp",
        prompt_version="240715-120000",
        input_tokens=100,
        output_tokens=50,
    )
    
    assert metrics.total_tokens_used == 150
    assert metrics.total_cost_usd >= 0.0
    assert metrics.average_response_time_ms > 0
    assert metrics.message_count == 1
    assert metrics.model_used == "gemini-2.5-flash-exp"
    assert metrics.prompt_version == "240715-120000"


def test_track_response_metrics_validation() -> None:
    """Test response metrics validation."""
    with pytest.raises(AssertionError, match="Start time must be positive"):
        track_response_metrics(
            start_time=0,
            model="gemini-2.5-flash-exp",
            prompt_version="240715-120000",
            input_tokens=100,
            output_tokens=50,
        )
    
    with pytest.raises(AssertionError, match="Model name cannot be empty"):
        track_response_metrics(
            start_time=time.time(),
            model="",
            prompt_version="v1.0",
            input_tokens=100,
            output_tokens=50,
        )
    
    with pytest.raises(AssertionError, match="Prompt version cannot be empty"):
        track_response_metrics(
            start_time=time.time(),
            model="gemini-2.5-flash-exp",
            prompt_version="",
            input_tokens=100,
            output_tokens=50,
        )
    
    with pytest.raises(AssertionError, match="Input tokens must be non-negative"):
        track_response_metrics(
            start_time=time.time(),
            model="gemini-2.5-flash-exp",
            prompt_version="v1.0",
            input_tokens=-1,
            output_tokens=50,
        )
    
    with pytest.raises(AssertionError, match="Output tokens must be non-negative"):
        track_response_metrics(
            start_time=time.time(),
            model="gemini-2.5-flash-exp",
            prompt_version="v1.0",
            input_tokens=100,
            output_tokens=-1,
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])