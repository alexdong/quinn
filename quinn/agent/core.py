"""Core AI agent functionality."""

from datetime import UTC, datetime
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult

from quinn.models import AgentConfig, Message
from quinn.models.response import MessageMetrics

from .cost import calculate_cost as litellm_calculate_cost

# Constants
MAX_PROMPT_LENGTH = 200


def _build_conversation_prompt(
    user_message: Message,
    conversation_history: list[Message],
) -> str:
    """Build conversation prompt from history and current message."""
    if not conversation_history:
        return user_message.user_content

    # Build conversation context from history
    conversation_messages = []
    for msg in conversation_history:
        if msg.user_content:
            conversation_messages.append(f"User: {msg.user_content}")
        if msg.assistant_content:
            conversation_messages.append(f"Assistant: {msg.assistant_content}")

    # Create prompt with conversation context
    return (
        "Previous conversation:\n"
        + "\n".join(conversation_messages)
        + "\n\nUser: "
        + user_message.user_content
    )


def _calculate_usage_metrics(
    result: AgentRunResult[Any], config: AgentConfig
) -> tuple[int, float]:
    """Calculate token usage and cost from result."""
    cost_usd = 0.0
    tokens_used = 0

    usage = result.usage()
    if usage:
        tokens_used = (usage.request_tokens or 0) + (usage.response_tokens or 0)
        if usage.request_tokens and usage.response_tokens:
            cost_usd = calculate_cost(
                model=config.model,
                input_tokens=usage.request_tokens,
                output_tokens=usage.response_tokens,
            )

    return tokens_used, cost_usd


async def generate_response(
    user_message: Message,
    conversation_history: list[Message] | None = None,
) -> Message:
    """Generate AI response with full error handling and metrics tracking."""
    assert user_message.user_content.strip(), "User message content cannot be empty"
    assert user_message.conversation_id.strip(), "Conversation ID cannot be empty"

    if conversation_history is None:
        conversation_history = []

    # Create agent with default config for now
    config = AgentConfig()
    agent = await create_agent(config)

    # Build conversation prompt
    prompt = _build_conversation_prompt(user_message, conversation_history)

    try:
        # Generate response using pydantic-ai
        start_time = datetime.now(UTC)
        result = await agent.run(prompt)
        end_time = datetime.now(UTC)

        # Calculate metrics
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)
        tokens_used, cost_usd = _calculate_usage_metrics(result, config)

        # Create response message with metadata
        return Message(
            assistant_content=str(result.output),
            conversation_id=user_message.conversation_id,
            system_prompt=prompt
            if len(prompt) <= MAX_PROMPT_LENGTH
            else prompt[:MAX_PROMPT_LENGTH] + "...",
            metadata=MessageMetrics(
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                response_time_ms=response_time_ms,
                model_used=config.model,
                prompt_version="240715-120000",  # Static for now
            ),
        )

    except Exception as e:
        # Create error response message
        return Message(
            assistant_content=f"Error generating response: {e!s}",
            conversation_id=user_message.conversation_id,
            system_prompt="Error occurred during response generation",
        )


async def create_agent(config: AgentConfig) -> Agent:
    """Create configured pydantic-ai agent instance."""
    assert isinstance(config, AgentConfig), "Config must be AgentConfig instance"

    # Map config to pydantic-ai settings
    model_settings = {
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "timeout": config.timeout_seconds,
    }

    # Create agent with configuration
    return Agent(
        config.model,
        model_settings=model_settings,
        retries=config.max_retries,
    )


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Calculate API cost based on token usage and model using litellm."""
    assert model.strip(), "Model name cannot be empty"
    assert input_tokens >= 0, "Input tokens must be non-negative"
    assert output_tokens >= 0, "Output tokens must be non-negative"

    return litellm_calculate_cost(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


if __name__ == "__main__":
    """Demonstrate agent core functionality."""
    import asyncio
    from uuid import uuid4

    from quinn.models import AgentConfig, Message

    async def main() -> None:
        """Demo the agent core functions."""
        print("🤖 Quinn Agent Core Demo")

        # Create sample configuration
        config = AgentConfig(
            model="claude-3.5-sonnet-20241022",
            temperature=0.7,
            max_tokens=1000,
        )
        print(f"📋 Config: {config.model}")

        # Create sample message
        message = Message(
            conversation_id=str(uuid4()),
            user_content="What's the best way to structure a Python project?",
        )
        print(f"📧 Message: {message.user_content[:50]}...")

        # Demonstrate cost calculation (this function works)
        cost = calculate_cost(
            model="claude-3-5-sonnet-20241022",
            input_tokens=100,
            output_tokens=200,
        )
        print(f"💰 Cost calculation: ${cost:.4f}")

        # Demo functions that need implementation
        try:
            agent = await create_agent(config)
            print(f"✅ Agent created: {agent}")
        except NotImplementedError as e:
            print(f"⚠️  Agent creation: {e}")

        try:
            response = await generate_response(message)
            print(f"✅ Response: {response.assistant_content[:50]}...")
        except NotImplementedError as e:
            print(f"⚠️  Response generation: {e}")

    asyncio.run(main())
