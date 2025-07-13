"""Core AI agent functionality."""

from pydantic_ai import Agent

from quinn.models import AgentConfig, AgentResponse, Message


async def generate_response(
    user_input: str,
    conversation_id: str,
    conversation_history: list[Message] | None = None,
) -> AgentResponse:
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
    input_tokens: int,
    output_tokens: int,
    config: AgentConfig,
) -> float:
    """Calculate API cost based on token usage and model."""
    assert input_tokens >= 0, "Input tokens must be non-negative"
    assert output_tokens >= 0, "Output tokens must be non-negative"
    assert isinstance(config, AgentConfig), "Config must be AgentConfig instance"

    input_cost = input_tokens * config.input_cost_per_token
    output_cost = output_tokens * config.output_cost_per_token

    return input_cost + output_cost
