"""Tests for AgentConfig model."""

import pytest

from .config import AgentConfig


def test_agent_config_default_values() -> None:
    """Test AgentConfig model with default values."""
    config = AgentConfig()
    assert config.model == "gemini/gemini-2.5-flash-exp"
    assert config.temperature == 0.7
    assert config.max_tokens == 4000
    assert config.timeout_seconds == 300
    assert config.max_retries == 3
    assert config.retry_backoff_factor == 2.0


def test_agent_config_custom_values() -> None:
    """Test AgentConfig model with custom values."""
    config = AgentConfig(
        model="claude-3.5-sonnet",
        temperature=0.5,
        max_tokens=2000,
        timeout_seconds=600,
        max_retries=5,
        retry_backoff_factor=1.5,
    )
    assert config.model == "claude-3.5-sonnet"
    assert config.temperature == 0.5
    assert config.max_tokens == 2000
    assert config.timeout_seconds == 600
    assert config.max_retries == 5
    assert config.retry_backoff_factor == 1.5


def test_agent_config_temperature_validation() -> None:
    """Test AgentConfig temperature validation."""
    with pytest.raises(ValueError):
        AgentConfig(temperature=-0.1)
    with pytest.raises(ValueError):
        AgentConfig(temperature=2.1)


def test_agent_config_max_tokens_validation() -> None:
    """Test AgentConfig max_tokens validation."""
    with pytest.raises(ValueError):
        AgentConfig(max_tokens=0)
    with pytest.raises(ValueError):
        AgentConfig(max_tokens=-1)


def test_agent_config_timeout_seconds_validation() -> None:
    """Test AgentConfig timeout_seconds validation."""
    with pytest.raises(ValueError):
        AgentConfig(timeout_seconds=0)
    with pytest.raises(ValueError):
        AgentConfig(timeout_seconds=-1)


def test_agent_config_max_retries_validation() -> None:
    """Test AgentConfig max_retries validation."""
    with pytest.raises(ValueError):
        AgentConfig(max_retries=-1)
    AgentConfig(max_retries=0)  # Should pass


def test_agent_config_retry_backoff_factor_validation() -> None:
    """Test AgentConfig retry_backoff_factor validation."""
    with pytest.raises(ValueError):
        AgentConfig(retry_backoff_factor=1.0)
    with pytest.raises(ValueError):
        AgentConfig(retry_backoff_factor=0.5)


def test_agent_config_empty_model_validation() -> None:
    """Test AgentConfig empty model validation."""
    with pytest.raises(ValueError, match="Model name cannot be empty"):
        AgentConfig(model="")
    with pytest.raises(ValueError, match="Model name cannot be empty"):
        AgentConfig(model="   ")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])