"""Core AI agent functionality."""

from pydantic_ai import Agent

from quinn.models import AgentConfig, Message

from .cost import calculate_cost as litellm_calculate_cost


async def generate_response(
    user_input: str,
    conversation_id: str,
    conversation_history: list[Message] | None = None,
) -> Message:
    """Generate AI response with full error handling and metrics tracking."""
    assert user_input.strip(), "User input cannot be empty"
    assert conversation_id.strip(), "Conversation ID cannot be empty"

    if conversation_history is None:
        conversation_history = []

    # TODO: Implement actual response generation
    msg = "Response generation not yet implemented"
    raise NotImplementedError(msg)


async def create_agent(config: AgentConfig) -> Agent:
    """Create configured pydantic-ai agent instance."""
    assert isinstance(config, AgentConfig), "Config must be AgentConfig instance"

    # TODO: Implement agent creation with pydantic-ai
    msg = "Agent creation not yet implemented"
    raise NotImplementedError(msg)


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Calculate API cost based on token usage and model using litellm."""
    return litellm_calculate_cost(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
