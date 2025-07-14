"""Test core AI agent functionality."""

import pytest

from quinn.models import AgentConfig, Message

from .core import calculate_cost, create_agent, generate_response


def test_calculate_cost() -> None:
    """Test cost calculation wrapper."""
    cost = calculate_cost(
        model="gemini-2.5-flash",
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
        calculate_cost("gemini-2.5-flash", -1, 50)

    with pytest.raises(AssertionError, match="Output tokens must be non-negative"):
        calculate_cost("gemini-2.5-flash", 100, -1)


@pytest.mark.asyncio
async def test_generate_response_basic() -> None:
    """Test basic response generation (may fail gracefully without API keys)."""
    message = Message(user_content="Hello", conversation_id="conv-123")
    response = await generate_response(message)

    assert isinstance(response, Message)
    assert response.conversation_id == "conv-123"
    assert response.assistant_content != ""

    # Response should either have metadata (success) or be an error message
    if response.assistant_content.startswith("Error generating response:"):
        # Error case - metadata is None but response is properly formatted
        assert response.metadata is None
        assert "Error generating response:" in response.assistant_content
    else:
        # Success case - should have metadata
        assert response.metadata is not None


@pytest.mark.asyncio
async def test_generate_response_with_history() -> None:
    """Test response generation with conversation history."""
    history = [
        Message(
            user_content="Hello",
            assistant_content="Hi there!",
            conversation_id="conv-123",
        ),
    ]
    message = Message(user_content="How are you?", conversation_id="conv-123")

    response = await generate_response(message, history)

    assert isinstance(response, Message)
    assert response.conversation_id == "conv-123"
    assert response.assistant_content != ""


@pytest.mark.asyncio
async def test_create_agent_validation() -> None:
    """Test create_agent input validation."""
    with pytest.raises(AssertionError, match="Config must be AgentConfig instance"):
        await create_agent("not-a-config")  # type: ignore


@pytest.mark.asyncio
async def test_create_agent_basic() -> None:
    """Test basic agent creation."""
    config = AgentConfig()
    agent = await create_agent(config)

    # Check that we got an Agent instance
    from pydantic_ai import Agent

    assert isinstance(agent, Agent)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
