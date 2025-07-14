"""Core AI agent functionality."""

from pydantic_ai import Agent

from quinn.models import AgentConfig, Message

from .cost import calculate_cost as litellm_calculate_cost


async def generate_response(
    user_message: Message,
    conversation_history: list[Message] | None = None,
) -> Message:
    """Generate AI response with full error handling and metrics tracking."""
    assert user_message.content.strip(), "User message content cannot be empty"
    assert user_message.conversation_id.strip(), "Conversation ID cannot be empty"

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
            content="What's the best way to structure a Python project?",
            role="user",
        )
        print(f"📧 Message: {message.content[:50]}...")

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
            print(f"✅ Response: {response.content[:50]}...")
        except NotImplementedError as e:
            print(f"⚠️  Response generation: {e}")

    asyncio.run(main())
