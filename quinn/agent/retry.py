"""Retry logic with exponential backoff."""

import asyncio
from collections.abc import Callable
from typing import TypeVar

from quinn.utils.logging import get_logger

T = TypeVar("T")

logger = get_logger(__name__)


async def retry_with_backoff[T](
    func: Callable[[], T],
    max_retries: int = 3,
    backoff_factor: float = 2.0,
) -> T:
    """Generic retry logic with exponential backoff."""
    assert max_retries >= 0, "Max retries must be non-negative"
    assert backoff_factor > 1.0, "Backoff factor must be > 1.0"

    logger.debug("Starting retry loop max_retries=%s", max_retries)

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            result = func()
            if asyncio.iscoroutine(result):
                return await result
            return result

        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                logger.error("Failed after %d attempts: %s", max_retries + 1, e)
                break

            delay = backoff_factor**attempt
            logger.warning(
                "Attempt %d failed: %s. Retrying in %ss",
                attempt + 1,
                e,
                delay,
            )
            await asyncio.sleep(delay)

    assert last_exception is not None, "Should have an exception if we reach here"
    raise last_exception
