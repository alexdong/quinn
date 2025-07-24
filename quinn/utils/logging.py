import asyncio
import contextvars
import logging
from collections.abc import Callable
from functools import wraps
from logging.handlers import RotatingFileHandler
from typing import ParamSpec, TypeVar
from uuid import uuid4

trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "trace_id", default="unknown"
)
span_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "span_id", default="-"
)


class ContextFilter(logging.Filter):
    """Inject trace information into log records."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - simple
        record.trace_id = trace_id_var.get()
        record.span_id = span_id_var.get()
        return True


def set_trace_id(mailbox_hash: str, message_id: str) -> str:
    """Set the trace ID using the mailbox hash and message ID."""
    trace_id = f"{mailbox_hash}:{message_id}"
    trace_id_var.set(trace_id)
    return trace_id


def span_for_llm(model: str, response_id: str) -> str:
    """Set span ID for an LLM response."""
    span = f"{model}:{response_id}"
    span_id_var.set(span)
    return span


def span_for_db(entity: str, entity_id: str) -> str:
    """Set span ID for a database operation."""
    span = f"{entity}:{entity_id}"
    span_id_var.set(span)
    return span


def generate_span_id() -> str:
    """Generate a generic span ID and store it in context."""
    span_id = uuid4().hex[:16]
    span_id_var.set(span_id)
    return span_id


def setup_logging(
    *,
    level: int = logging.INFO,
    log_file: str = "quinn.log",
    debug_modules: list[str] | None = None,
) -> None:
    """Configure application logging."""
    logging.getLogger().handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s][%(levelname)s][%(name)s][%(trace_id)s][%(span_id)s] %(message)s"
    )

    handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(formatter)
    handler.addFilter(ContextFilter())

    logging.basicConfig(level=level, handlers=[handler])

    if debug_modules:
        for mod in debug_modules:
            logging.getLogger(mod).setLevel(logging.DEBUG)


P = ParamSpec("P")
T = TypeVar("T")


def trace(func: Callable[P, T]) -> Callable[P, T]:  # noqa: UP047
    """Decorator to create a new span for the wrapped call."""

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            generate_span_id()
            return await func(*args, **kwargs)

        return async_wrapper

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        generate_span_id()
        return func(*args, **kwargs)

    return wrapper


if __name__ == "__main__":  # pragma: no cover - manual test
    setup_logging(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    @trace
    def demo() -> None:
        logger.debug("Demo function executed")

    demo()
