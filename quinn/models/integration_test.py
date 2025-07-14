"""Integration tests for model interactions."""

from .conversation import Conversation, Message
from .prompt import PromptContext
from .response import AgentResponse, ConversationMetrics


def test_conversation_with_metrics() -> None:
    """Test Conversation integration with ConversationMetrics."""
    metrics = ConversationMetrics(
        total_tokens_used=500,
        model_used="gpt-4",
        prompt_version="240715-120000",
    )
    
    conversation = Conversation(metrics=metrics)
    assert conversation.metrics == metrics
    assert conversation.metrics.total_tokens_used == 500


def test_prompt_context_with_messages() -> None:
    """Test PromptContext integration with Message history."""
    messages = [
        Message(content="Hello", role="user"),
        Message(content="Hi!", role="assistant"),
    ]
    
    context = PromptContext(
        user_input="How are you?",
        conversation_history=messages,
        prompt_version="240715-120000",
        system_prompt="Be helpful",
    )
    
    assert len(context.conversation_history) == 2
    assert context.conversation_history[0].role == "user"
    assert context.conversation_history[1].role == "assistant"


def test_complete_workflow() -> None:
    """Test complete integration workflow across all models."""
    # Create conversation
    conversation = Conversation()
    
    # Add user message
    user_message = Message(content="What is AI?", role="user")
    conversation.add_message(user_message)
    
    # Create prompt context
    context = PromptContext(
        user_input="What is AI?",
        conversation_history=conversation.messages,
        prompt_version="240715-120000",
        system_prompt="You are an AI assistant",
    )
    
    # Create agent response
    response = AgentResponse(
        content="AI stands for Artificial Intelligence...",
        conversation_id=conversation.id,
        message_id=user_message.id,
        tokens_used=75,
        cost_usd=0.001,
        response_time_ms=850,
        model_used="gpt-4",
        prompt_version="240715-120000",
    )
    
    # Add assistant message to conversation
    assistant_message = Message(
        content=response.content,
        role="assistant",
    )
    conversation.add_message(assistant_message)
    
    # Create metrics
    metrics = ConversationMetrics(
        total_tokens_used=response.tokens_used,
        total_cost_usd=response.cost_usd,
        average_response_time_ms=response.response_time_ms,
        message_count=len(conversation.messages),
        model_used=response.model_used,
        prompt_version=response.prompt_version,
    )
    conversation.metrics = metrics
    
    # Verify complete workflow
    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == "user"
    assert conversation.messages[1].role == "assistant"
    assert conversation.metrics.message_count == 2
    assert response.conversation_id == conversation.id
    assert response.message_id == user_message.id


def test_conversation_message_history_flow() -> None:
    """Test message history flow through conversation and prompt context."""
    # Start with empty conversation
    conversation = Conversation()
    
    # Add several messages
    msg1 = Message(content="Hello", role="user")
    msg2 = Message(content="Hi there!", role="assistant")
    msg3 = Message(content="How can you help?", role="user")
    
    conversation.add_message(msg1)
    conversation.add_message(msg2)
    conversation.add_message(msg3)
    
    # Use conversation history in prompt context
    context = PromptContext(
        user_input="I need help with code",
        conversation_history=conversation.messages,
        prompt_version="240715-120000",
        system_prompt="You are a coding assistant",
    )
    
    # Verify integration
    assert len(context.conversation_history) == 3
    assert context.conversation_history == conversation.messages
    assert conversation.get_latest_message() == msg3
    assert len(conversation.get_messages_by_role("user")) == 2
    assert len(conversation.get_messages_by_role("assistant")) == 1


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])