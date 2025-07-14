"""Integration tests for model interactions."""

from .conversation import Conversation, Message
from .response import ConversationMetrics, MessageMetrics


def test_conversation_with_metrics() -> None:
    """Test Conversation integration with ConversationMetrics."""
    metrics = ConversationMetrics(
        total_tokens_used=500,
        model_used="gpt-4",
        prompt_version="240715-120000",
    )
    
    conversation = Conversation(metrics=metrics)
    assert conversation.metrics == metrics
    assert conversation.metrics is not None
    assert conversation.metrics.total_tokens_used == 500


def test_message_with_system_prompt() -> None:
    """Test Message with system prompt functionality."""
    message = Message(
        content="How are you?",
        role="user",
        system_prompt="Be helpful and friendly",
    )
    
    assert message.content == "How are you?"
    assert message.system_prompt == "Be helpful and friendly"
    assert message.role == "user"


def test_complete_workflow() -> None:
    """Test complete integration workflow across all models."""
    # Create conversation
    conversation = Conversation()
    
    # Add user message with system prompt
    user_message = Message(
        content="What is AI?",
        role="user",
        system_prompt="You are an AI assistant",
        conversation_id=conversation.id,
    )
    conversation.add_message(user_message)
    
    # Create assistant message with metrics
    assistant_message = Message(
        content="AI stands for Artificial Intelligence...",
        role="assistant",
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
    assert conversation.messages[0].role == "user"
    assert conversation.messages[1].role == "assistant"
    assert conversation.metrics is not None
    assert conversation.metrics.message_count == 2
    assert conversation.metrics.total_tokens_used == 75
    assert assistant_message.conversation_id == conversation.id


def test_conversation_message_history_flow() -> None:
    """Test message history flow through conversation."""
    # Start with empty conversation
    conversation = Conversation()
    
    # Add several messages
    msg1 = Message(content="Hello", role="user")
    msg2 = Message(content="Hi there!", role="assistant")
    msg3 = Message(content="How can you help?", role="user", system_prompt="Be helpful")
    
    conversation.add_message(msg1)
    conversation.add_message(msg2)
    conversation.add_message(msg3)
    
    # Verify integration
    assert len(conversation.messages) == 3
    assert conversation.get_latest_message() == msg3
    assert len(conversation.get_messages_by_role("user")) == 2
    assert len(conversation.get_messages_by_role("assistant")) == 1
    assert msg3.system_prompt == "Be helpful"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])