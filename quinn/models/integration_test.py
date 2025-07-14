"""Integration tests for model interactions."""

from .conversation import Conversation, ConversationMetrics
from .message import Message, MessageMetrics


def test_conversation_with_metrics() -> None:
    """Test Conversation integration with ConversationMetrics."""
    metrics = ConversationMetrics(
        total_tokens_used=500,
        model_used="gpt-4",
        prompt_version="240715-120000",
    )
    
    conversation = Conversation()
    conversation.add_message(Message(user_content="test", metadata=MessageMetrics(model_used=metrics.model_used, prompt_version=metrics.prompt_version, tokens_used=metrics.total_tokens_used, cost_usd=metrics.total_cost_usd, response_time_ms=metrics.average_response_time_ms)))
    
    # Check metrics exist first
    assert conversation.metrics is not None
    assert conversation.metrics.total_tokens_used == metrics.total_tokens_used
    assert conversation.metrics.model_used == metrics.model_used
    assert conversation.metrics.prompt_version == metrics.prompt_version
    assert conversation.metrics.total_tokens_used == 500


def test_message_with_system_prompt() -> None:
    """Test Message with system prompt functionality."""
    message = Message(
        user_content="How are you?",
        system_prompt="Be helpful and friendly",
    )
    
    assert message.user_content == "How are you?"
    assert message.system_prompt == "Be helpful and friendly"


def test_complete_workflow() -> None:
    """Test complete integration workflow across all models."""
    # Create conversation
    conversation = Conversation()
    
    # Add user message with system prompt
    user_message = Message(
        user_content="What is AI?",
        system_prompt="You are an AI assistant",
        conversation_id=conversation.id,
    )
    conversation.add_message(user_message)
    
    # Create assistant message with metrics
    assistant_message = Message(
        user_content="What is AI?",
        assistant_content="AI stands for Artificial Intelligence...",
        conversation_id=conversation.id,
        metadata=MessageMetrics(
            tokens_used=75,
            cost_usd=0.001,
            response_time_ms=850,
            model_used="gpt-4",
            prompt_version="240715-120000",
        ),
    )
    conversation.add_message(assistant_message)
    
    # Verify complete workflow
    assert len(conversation.messages) == 2
    assert conversation.messages[0].user_content == "What is AI?"
    assert conversation.messages[1].assistant_content == "AI stands for Artificial Intelligence..."
    assert conversation.metrics is not None
    assert conversation.metrics.message_count == 2
    assert conversation.metrics.total_tokens_used == 75
    assert assistant_message.conversation_id == conversation.id


def test_conversation_message_history_flow() -> None:
    """Test message history flow through conversation."""
    # Start with empty conversation
    conversation = Conversation()
    
    # Add several messages
    msg1 = Message(user_content="Hello")
    msg2 = Message(assistant_content="Hi there!")
    msg3 = Message(user_content="How can you help?", system_prompt="Be helpful")
    
    conversation.add_message(msg1)
    conversation.add_message(msg2)
    conversation.add_message(msg3)
    
    # Verify integration
    assert len(conversation.messages) == 3
    assert conversation.get_latest_message() == msg3
    assert msg3.system_prompt == "Be helpful"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])