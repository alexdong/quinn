import logging
import pytest
from importlib import reload
from pathlib import Path

from . import logging as logging_utils


def test_set_ids() -> None:
    trace_id = logging_utils.set_trace_id("box", "msg")
    span_id1 = logging_utils.span_for_llm("gpt4", "resp123")
    assert trace_id == "box:msg"
    assert logging_utils.trace_id_var.get() == "box:msg"
    assert span_id1 == "gpt4:resp123"
    assert logging_utils.span_id_var.get() == "gpt4:resp123"
    span_id2 = logging_utils.span_for_db("users", "42")
    assert span_id2 == "users:42"
    assert logging_utils.span_id_var.get() == "users:42"


def test_trace_wraps() -> None:
    @logging_utils.trace
    def sample() -> str:
        return "ok"

    assert getattr(sample, "__name__", "") == "sample"
    assert sample() == "ok"


def test_setup_logging_debug_modules(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    logging_utils.setup_logging(
        level=logging.INFO, log_file=str(log_file), debug_modules=["test.mod"]
    )
    logger = logging.getLogger("test.mod")
    assert logger.level == logging.DEBUG
    assert log_file.exists()
    reload(logging_utils)  # reset for other tests


def test_setup_logging_no_debug_modules(tmp_path: Path) -> None:
    """Coverage for branch when no debug modules provided."""
    log_file = tmp_path / "nodebug.log"
    logging_utils.setup_logging(level=logging.INFO, log_file=str(log_file))
    logging.getLogger("nodebug").info("hi")
    assert log_file.exists()
    reload(logging_utils)


def test_get_logger_filter_added() -> None:
    """Ensure context filter is added exactly once."""
    logger = logging_utils.get_logger("foo")
    assert any(isinstance(f, logging_utils.ContextFilter) for f in logger.filters)
    logger_again = logging_utils.get_logger("foo")
    assert logger is logger_again
    count = sum(isinstance(f, logging_utils.ContextFilter) for f in logger.filters)
    assert count == 1


@pytest.mark.asyncio
async def test_trace_async() -> None:
    """Async function should get a fresh span id on each call."""

    @logging_utils.trace
    async def sample() -> str:
        return logging_utils.span_id_var.get()

    first = await sample()
    second = await sample()
    assert len(first) == 16
    assert len(second) == 16
    assert first != second
    assert logging_utils.span_id_var.get() == second
