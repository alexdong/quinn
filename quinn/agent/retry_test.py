"""Test retry logic with exponential backoff."""

import asyncio
import time
from unittest.mock import patch

import pytest

from .retry import retry_with_backoff


@pytest.mark.asyncio
async def test_retry_with_backoff_success() -> None:
    """Test successful function execution without retries."""
    
    def successful_func() -> str:
        return "success"
    
    result = await retry_with_backoff(successful_func)
    assert result == "success"


@pytest.mark.asyncio
async def test_retry_with_backoff_async_success() -> None:
    """Test successful async function execution without retries."""
    
    async def successful_async_func() -> str:
        return "async_success"
    
    result = await retry_with_backoff(successful_async_func)
    assert result == "async_success"


@pytest.mark.asyncio
async def test_retry_with_backoff_eventual_success() -> None:
    """Test function that fails initially but eventually succeeds."""
    
    class Counter:
        def __init__(self) -> None:
            self.count = 0
    
    counter = Counter()
    
    def flaky_func() -> str:
        counter.count += 1
        if counter.count < 3:
            raise ValueError(f"Attempt {counter.count} failed")
        return "eventually_success"
    
    # Mock asyncio.sleep to avoid actual delays
    with patch('asyncio.sleep', return_value=None):
        result = await retry_with_backoff(flaky_func, max_retries=3, backoff_factor=1.1)
        assert result == "eventually_success"
        assert counter.count == 3


@pytest.mark.asyncio
async def test_retry_with_backoff_max_retries_exceeded() -> None:
    """Test function that always fails and exhausts retries."""
    
    class Counter:
        def __init__(self) -> None:
            self.count = 0
    
    counter = Counter()
    
    def always_fails() -> str:
        counter.count += 1
        raise RuntimeError(f"Failure {counter.count}")
    
    # Mock asyncio.sleep to avoid actual delays
    with patch('asyncio.sleep', return_value=None):
        with pytest.raises(RuntimeError, match="Failure 4"):
            await retry_with_backoff(always_fails, max_retries=3, backoff_factor=1.1)
        
        assert counter.count == 4  # Initial attempt + 3 retries


@pytest.mark.asyncio
async def test_retry_with_backoff_timing() -> None:
    """Test that backoff timing works correctly."""
    
    class TimedCounter:
        def __init__(self) -> None:
            self.call_times: list[float] = []
            self.sleep_delays: list[float] = []
    
    timed_counter = TimedCounter()
    
    def timed_func() -> str:
        timed_counter.call_times.append(time.time())
        if len(timed_counter.call_times) < 3:
            raise ValueError("Not yet")
        return "success"
    
    # Mock asyncio.sleep to capture delays without waiting
    async def mock_sleep(delay: float) -> None:
        timed_counter.sleep_delays.append(delay)
    
    with patch('asyncio.sleep', side_effect=mock_sleep):
        result = await retry_with_backoff(timed_func, max_retries=3, backoff_factor=2.0)
        
        assert result == "success"
        assert len(timed_counter.call_times) == 3
        
        # Verify backoff delays: 2^0=1, 2^1=2
        assert len(timed_counter.sleep_delays) == 2
        assert timed_counter.sleep_delays[0] == 1.0  # 2^0
        assert timed_counter.sleep_delays[1] == 2.0  # 2^1


@pytest.mark.asyncio
async def test_retry_with_backoff_validation() -> None:
    """Test retry function validation."""
    
    def dummy_func() -> str:
        return "test"
    
    with pytest.raises(AssertionError, match="Max retries must be non-negative"):
        await retry_with_backoff(dummy_func, max_retries=-1)
    
    with pytest.raises(AssertionError, match="Backoff factor must be > 1.0"):
        await retry_with_backoff(dummy_func, backoff_factor=1.0)
    
    with pytest.raises(AssertionError, match="Backoff factor must be > 1.0"):
        await retry_with_backoff(dummy_func, backoff_factor=0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])