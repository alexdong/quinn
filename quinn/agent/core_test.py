"""Test core AI agent functionality."""

import pytest

from quinn.models import AgentConfig, Message

from .core import calculate_cost, create_agent, generate_response


def test_calculate_cost() -> None:
    """Test cost calculation wrapper."""
    cost = calculate_cost(
        model="gemini/gemini-2.5-flash-exp",
        input_tokens=1000,
        output_tokens=500,
    )
    
    assert isinstance(cost, float)
    assert cost >= 0.0


def test_calculate_cost_validation() -> None:
    """Test cost calculation input validation."""
    with pytest.raises(AssertionError, match="Model name cannot be empty"):
        calculate_cost("", 100, 50)
        
    with pytest.raises(AssertionError, match="Input tokens must be non-negative"):
        calculate_cost("gemini/gemini-2.5-flash-exp", -1, 50)
        
    with pytest.raises(AssertionError, match="Output tokens must be non-negative"):
        calculate_cost("gemini/gemini-2.5-flash-exp", 100, -1)


@pytest.mark.asyncio
async def test_generate_response_validation() -> None:
    """Test generate_response input validation."""
    with pytest.raises(AssertionError, match="User input cannot be empty"):
        await generate_response("", "conv-123")
        
    with pytest.raises(AssertionError, match="Conversation ID cannot be empty"):
        await generate_response("Hello", "")


@pytest.mark.asyncio
async def test_generate_response_not_implemented() -> None:
    """Test that generate_response raises NotImplementedError."""
    with pytest.raises(NotImplementedError, match="Response generation not yet implemented"):
        await generate_response("Hello", "conv-123")


@pytest.mark.asyncio
async def test_create_agent_validation() -> None:
    """Test create_agent input validation."""
    with pytest.raises(AssertionError, match="Config must be AgentConfig instance"):
        await create_agent("not-a-config")  # type: ignore


@pytest.mark.asyncio
async def test_create_agent_not_implemented() -> None:
    """Test that create_agent raises NotImplementedError."""
    config = AgentConfig()
    with pytest.raises(NotImplementedError, match="Agent creation not yet implemented"):
        await create_agent(config)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])