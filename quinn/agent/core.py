"""Core AI agent functionality."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NamedTuple

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.settings import ModelSettings

from quinn.models import AgentConfig, Message
from quinn.models.message import MessageMetrics

from .cost import calculate_cost


class UsageMetrics(NamedTuple):
    """Detailed usage metrics breakdown."""

    input_tokens: int
    output_tokens: int
    cached_tokens: int
    total_tokens: int
    total_cost_usd: float


# Constants
MAX_PROMPT_LENGTH = 20000


def _load_system_prompt() -> str:
    """Load the system prompt from the templates directory."""
    prompt_path = Path(__file__).parent.parent / "templates" / "prompts" / "system_prompt.txt"
    try:
        return prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        # Fallback to basic prompt if file not found
        return "You are Quinn, a helpful AI assistant that guides users to solve their own problems by asking thoughtful questions rather than providing direct solutions."


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
        "Previous conversations:\n"
        + "\n".join(conversation_messages)
        + "\n\nUser: "
        + user_message.user_content
    )


def _calculate_usage_metrics(
    result: AgentRunResult[Any], config: AgentConfig
) -> UsageMetrics:
    """Calculate detailed token usage and cost breakdown from result."""
    usage = result.usage()
    assert usage, "Usage information is required for metrics calculation"

    input_tokens = usage.request_tokens or 0
    output_tokens = usage.response_tokens or 0

    # Extract cached tokens from details if available
    cached_tokens = 0
    if usage.details:
        # Common keys for cached tokens across different providers
        cached_keys = ["cache_read_input_tokens", "cached_tokens", "cache_tokens"]
        for key in cached_keys:
            if key in usage.details:
                cached_tokens = usage.details[key]
                break

    total_tokens = usage.total_tokens or (input_tokens + output_tokens)

    # Calculate cost
    cost_usd = 0.0
    assert input_tokens >= 0, "Input tokens must be non-negative"
    assert output_tokens >= 0, "Output tokens must be non-negative"
    cost_usd = calculate_cost(
        model=config.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )

    return UsageMetrics(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        total_tokens=total_tokens,
        total_cost_usd=cost_usd,
    )


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
    config = AgentConfig.o4mini()
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
        usage_metrics = _calculate_usage_metrics(result, config)

        # Create response message with metadata
        return Message(
            user_content=user_message.user_content,
            assistant_content=str(result.output),
            conversation_id=user_message.conversation_id,
            created_at=start_time,  # When sent to LLM
            last_updated_at=end_time,  # When response received
            system_prompt=user_message.system_prompt
            or (
                prompt
                if len(prompt) <= MAX_PROMPT_LENGTH
                else prompt[:MAX_PROMPT_LENGTH] + "..."
            ),
            metadata=MessageMetrics(
                tokens_used=usage_metrics.total_tokens,
                cost_usd=usage_metrics.total_cost_usd,
                response_time_ms=response_time_ms,
                model_used=config.model,
                prompt_version="240715-120000",  # Static for now
            ),
        )

    except Exception as e:
        # Create error response message
        error_time = datetime.now(UTC)
        return Message(
            user_content=user_message.user_content,
            assistant_content=f"Error generating response: {e!s}",
            conversation_id=user_message.conversation_id,
            created_at=start_time,  # When sent to LLM
            last_updated_at=error_time,  # When error occurred
            system_prompt="Error occurred during response generation",
        )


async def create_agent(config: AgentConfig) -> Agent:
    """Create configured pydantic-ai agent instance."""
    assert isinstance(config, AgentConfig), "Config must be AgentConfig instance"

    # Map config to pydantic-ai settings
    model_settings = ModelSettings(
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        timeout_seconds=config.timeout_seconds,
        max_retries=config.max_retries,
        retry_backoff_factor=config.retry_backoff_factor,
    )

    # Create agent with configuration
    return Agent(
        model=config.model,
        system_prompt=_load_system_prompt(),
        model_settings=model_settings,
        retries=config.max_retries,
    )


if __name__ == "__main__":
    """Demonstrate agent core functionality."""
    import asyncio
    from uuid import uuid4

    from quinn.models import AgentConfig, Message

    async def main() -> None:
        """Demo the agent core functions."""
        print("\n🔧 Testing Quinn core functions...")

        conversation_id = str(uuid4())

        # Create sample configuration
        config = AgentConfig.o4mini()
        print(f"📋 Config: {config.model}")

        # Create sample message
        message = Message(
            conversation_id=conversation_id,
            user_content="What's the capital of France?",
        )
        print(f"📧 Message: {message.user_content}")

        agent = await create_agent(config)
        print(f"✅ Agent created: {agent}")
        message = await generate_response(message)
        print(f"✅ Response: {message.assistant_content}")
        print(
            f"✅ Response contains expected content: {'Paris' in message.assistant_content}"
        )

        if message.metadata:
            print(f"📊 Metadata: {message.metadata}")
        else:
            print("📊 No metadata available")

    asyncio.run(main())
