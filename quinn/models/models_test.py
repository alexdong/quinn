"""Comprehensive tests for all Quinn data models."""

import uuid
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from .config import AgentConfig
from .conversation import Conversation, Message
from .prompt import PromptContext
from .response import AgentResponse, ConversationMetrics

# Rebuild models to resolve forward references
Conversation.model_rebuild()
PromptContext.model_rebuild()


class TestAgentConfig:
    """Test AgentConfig model."""

    def test_default_values(self) -> None:
        config = AgentConfig()
        assert config.model == "gemini/gemini-2.5-flash-exp"
        assert config.temperature == 0.7
        assert config.max_tokens == 4000
        assert config.timeout_seconds == 300
        assert config.max_retries == 3
        assert config.retry_backoff_factor == 2.0

    def test_custom_values(self) -> None:
        config = AgentConfig(
            model="claude-3.5-sonnet",
            temperature=0.5,
            max_tokens=2000,
            timeout_seconds=600,
            max_retries=5,
            retry_backoff_factor=1.5,
        )
        assert config.model == "claude-3.5-sonnet"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
        assert config.timeout_seconds == 600
        assert config.max_retries == 5
        assert config.retry_backoff_factor == 1.5

    def test_temperature_validation(self) -> None:
        with pytest.raises(ValueError):
            AgentConfig(temperature=-0.1)
        with pytest.raises(ValueError):
            AgentConfig(temperature=2.1)

    def test_max_tokens_validation(self) -> None:
        with pytest.raises(ValueError):
            AgentConfig(max_tokens=0)
        with pytest.raises(ValueError):
            AgentConfig(max_tokens=-1)

    def test_timeout_seconds_validation(self) -> None:
        with pytest.raises(ValueError):
            AgentConfig(timeout_seconds=0)
        with pytest.raises(ValueError):
            AgentConfig(timeout_seconds=-1)

    def test_max_retries_validation(self) -> None:
        with pytest.raises(ValueError):
            AgentConfig(max_retries=-1)
        AgentConfig(max_retries=0)  # Should pass

    def test_retry_backoff_factor_validation(self) -> None:
        with pytest.raises(ValueError):
            AgentConfig(retry_backoff_factor=1.0)
        with pytest.raises(ValueError):
            AgentConfig(retry_backoff_factor=0.5)

    def test_empty_model_validation(self) -> None:
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            AgentConfig(model="")
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            AgentConfig(model="   ")


class TestMessage:
    """Test Message model."""

    def test_default_values(self) -> None:
        message = Message(content="Hello world")
        assert message.role == "user"
        assert message.content == "Hello world"
        assert message.metadata == {}
        assert isinstance(message.id, str)
        assert len(message.id) == 36  # UUID4 length
        assert isinstance(message.timestamp, datetime)

    def test_custom_values(self) -> None:
        custom_time = datetime.now(UTC)
        custom_metadata = {"key": "value", "number": 42}
        
        message = Message(
            role="assistant",
            content="AI response",
            timestamp=custom_time,
            metadata=custom_metadata,
        )
        assert message.role == "assistant"
        assert message.content == "AI response"
        assert message.timestamp == custom_time
        assert message.metadata == custom_metadata

    def test_uuid_generation(self) -> None:
        message1 = Message(content="Test 1")
        message2 = Message(content="Test 2")
        assert message1.id != message2.id
        assert uuid.UUID(message1.id)  # Should not raise
        assert uuid.UUID(message2.id)  # Should not raise

    def test_empty_content_validation(self) -> None:
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            Message(content="")
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            Message(content="   ")

    def test_metadata_types(self) -> None:
        metadata = {
            "string": "value",
            "int": 42,
            "float": 3.14,
            "bool": True,
        }
        message = Message(content="Test", metadata=metadata)
        assert message.metadata == metadata


class TestConversation:
    """Test Conversation model."""

    def test_default_values(self) -> None:
        conversation = Conversation()
        assert conversation.messages == []
        assert conversation.metrics is None
        assert isinstance(conversation.id, str)
        assert len(conversation.id) == 36  # UUID4 length
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)

    def test_add_message(self) -> None:
        conversation = Conversation()
        original_updated_at = conversation.updated_at
        
        message = Message(content="Hello")
        conversation.add_message(message)
        
        assert len(conversation.messages) == 1
        assert conversation.messages[0] == message
        assert conversation.updated_at > original_updated_at

    def test_get_latest_message(self) -> None:
        conversation = Conversation()
        assert conversation.get_latest_message() is None
        
        message1 = Message(content="First")
        message2 = Message(content="Second")
        
        conversation.add_message(message1)
        assert conversation.get_latest_message() == message1
        
        conversation.add_message(message2)
        assert conversation.get_latest_message() == message2

    def test_get_messages_by_role(self) -> None:
        conversation = Conversation()
        
        user_msg1 = Message(content="User 1", role="user")
        assistant_msg = Message(content="Assistant", role="assistant")
        user_msg2 = Message(content="User 2", role="user")
        
        conversation.add_message(user_msg1)
        conversation.add_message(assistant_msg)
        conversation.add_message(user_msg2)
        
        user_messages = conversation.get_messages_by_role("user")
        assistant_messages = conversation.get_messages_by_role("assistant")
        
        assert len(user_messages) == 2
        assert len(assistant_messages) == 1
        assert user_messages == [user_msg1, user_msg2]
        assert assistant_messages == [assistant_msg]

    def test_uuid_generation(self) -> None:
        conv1 = Conversation()
        conv2 = Conversation()
        assert conv1.id != conv2.id
        assert uuid.UUID(conv1.id)  # Should not raise
        assert uuid.UUID(conv2.id)  # Should not raise


class TestPromptContext:
    """Test PromptContext model."""

    def test_default_values(self) -> None:
        context = PromptContext(
            user_input="Hello",
            prompt_version="v1.0",
            system_prompt="You are helpful",
        )
        assert context.user_input == "Hello"
        assert context.prompt_version == "v1.0"
        assert context.system_prompt == "You are helpful"
        assert context.conversation_history == []
        assert isinstance(context.id, str)
        assert len(context.id) == 36  # UUID4 length

    def test_with_conversation_history(self) -> None:
        messages = [
            Message(content="Hello", role="user"),
            Message(content="Hi there!", role="assistant"),
        ]
        
        context = PromptContext(
            user_input="How are you?",
            conversation_history=messages,
            prompt_version="v1.0",
            system_prompt="You are helpful",
        )
        assert context.conversation_history == messages

    def test_empty_field_validation(self) -> None:
        with pytest.raises(ValueError, match="Field cannot be empty"):
            PromptContext(user_input="", prompt_version="v1", system_prompt="test")
        
        with pytest.raises(ValueError, match="Field cannot be empty"):
            PromptContext(user_input="test", prompt_version="", system_prompt="test")
        
        with pytest.raises(ValueError, match="Field cannot be empty"):
            PromptContext(user_input="test", prompt_version="v1", system_prompt="")

    def test_whitespace_validation(self) -> None:
        with pytest.raises(ValueError, match="Field cannot be empty"):
            PromptContext(user_input="   ", prompt_version="v1", system_prompt="test")

    def test_uuid_generation(self) -> None:
        context1 = PromptContext(user_input="test1", prompt_version="v1", system_prompt="test")
        context2 = PromptContext(user_input="test2", prompt_version="v1", system_prompt="test")
        assert context1.id != context2.id
        assert uuid.UUID(context1.id)  # Should not raise
        assert uuid.UUID(context2.id)  # Should not raise


class TestConversationMetrics:
    """Test ConversationMetrics model."""

    def test_default_values(self) -> None:
        metrics = ConversationMetrics(model_used="gpt-4", prompt_version="v1.0")
        assert metrics.total_tokens_used == 0
        assert metrics.total_cost_usd == 0.0
        assert metrics.average_response_time_ms == 0
        assert metrics.message_count == 0
        assert metrics.model_used == "gpt-4"
        assert metrics.prompt_version == "v1.0"

    def test_custom_values(self) -> None:
        metrics = ConversationMetrics(
            total_tokens_used=1500,
            total_cost_usd=0.025,
            average_response_time_ms=750,
            message_count=3,
            model_used="claude-3.5-sonnet",
            prompt_version="v2.1",
        )
        assert metrics.total_tokens_used == 1500
        assert metrics.total_cost_usd == 0.025
        assert metrics.average_response_time_ms == 750
        assert metrics.message_count == 3
        assert metrics.model_used == "claude-3.5-sonnet"
        assert metrics.prompt_version == "v2.1"

    def test_negative_value_validation(self) -> None:
        with pytest.raises(ValueError):
            ConversationMetrics(total_tokens_used=-1, model_used="gpt-4", prompt_version="v1")
        
        with pytest.raises(ValueError):
            ConversationMetrics(total_cost_usd=-0.01, model_used="gpt-4", prompt_version="v1")
        
        with pytest.raises(ValueError):
            ConversationMetrics(average_response_time_ms=-1, model_used="gpt-4", prompt_version="v1")
        
        with pytest.raises(ValueError):
            ConversationMetrics(message_count=-1, model_used="gpt-4", prompt_version="v1")

    def test_empty_string_validation(self) -> None:
        with pytest.raises(ValueError, match="Field cannot be empty"):
            ConversationMetrics(model_used="", prompt_version="v1")
        
        with pytest.raises(ValueError, match="Field cannot be empty"):
            ConversationMetrics(model_used="gpt-4", prompt_version="")

    def test_whitespace_validation(self) -> None:
        with pytest.raises(ValueError, match="Field cannot be empty"):
            ConversationMetrics(model_used="   ", prompt_version="v1")


class TestAgentResponse:
    """Test AgentResponse model."""

    def test_default_values(self) -> None:
        response = AgentResponse(
            content="Hello!",
            conversation_id="conv-123",
            message_id="msg-456",
        )
        assert response.content == "Hello!"
        assert response.conversation_id == "conv-123"
        assert response.message_id == "msg-456"
        assert response.tokens_used == 0
        assert response.cost_usd == 0.0
        assert response.response_time_ms == 0
        assert response.model_used == ""
        assert response.prompt_version == ""
        assert isinstance(response.id, str)
        assert len(response.id) == 36  # UUID4 length

    def test_custom_values(self) -> None:
        response = AgentResponse(
            content="AI response here",
            conversation_id="conv-789",
            message_id="msg-101",
            tokens_used=250,
            cost_usd=0.005,
            response_time_ms=1200,
            model_used="gpt-4-turbo",
            prompt_version="v1.5",
        )
        assert response.content == "AI response here"
        assert response.conversation_id == "conv-789"
        assert response.message_id == "msg-101"
        assert response.tokens_used == 250
        assert response.cost_usd == 0.005
        assert response.response_time_ms == 1200
        assert response.model_used == "gpt-4-turbo"
        assert response.prompt_version == "v1.5"

    def test_negative_value_validation(self) -> None:
        with pytest.raises(ValueError):
            AgentResponse(
                content="test",
                conversation_id="conv",
                message_id="msg",
                tokens_used=-1,
            )
        
        with pytest.raises(ValueError):
            AgentResponse(
                content="test",
                conversation_id="conv",
                message_id="msg",
                cost_usd=-0.01,
            )
        
        with pytest.raises(ValueError):
            AgentResponse(
                content="test",
                conversation_id="conv",
                message_id="msg",
                response_time_ms=-1,
            )

    def test_empty_string_validation(self) -> None:
        with pytest.raises(ValueError, match="Field cannot be empty"):
            AgentResponse(content="", conversation_id="conv", message_id="msg")
        
        with pytest.raises(ValueError, match="Field cannot be empty"):
            AgentResponse(content="test", conversation_id="", message_id="msg")
        
        with pytest.raises(ValueError, match="Field cannot be empty"):
            AgentResponse(content="test", conversation_id="conv", message_id="")

    def test_whitespace_validation(self) -> None:
        with pytest.raises(ValueError, match="Field cannot be empty"):
            AgentResponse(content="   ", conversation_id="conv", message_id="msg")

    def test_uuid_generation(self) -> None:
        response1 = AgentResponse(content="test1", conversation_id="conv", message_id="msg")
        response2 = AgentResponse(content="test2", conversation_id="conv", message_id="msg")
        assert response1.id != response2.id
        assert uuid.UUID(response1.id)  # Should not raise
        assert uuid.UUID(response2.id)  # Should not raise


class TestModelIntegration:
    """Test integration between models."""

    def test_conversation_with_metrics(self) -> None:
        metrics = ConversationMetrics(
            total_tokens_used=500,
            model_used="gpt-4",
            prompt_version="v1.0",
        )
        
        conversation = Conversation(metrics=metrics)
        assert conversation.metrics == metrics
        assert conversation.metrics.total_tokens_used == 500

    def test_prompt_context_with_messages(self) -> None:
        messages = [
            Message(content="Hello", role="user"),
            Message(content="Hi!", role="assistant"),
        ]
        
        context = PromptContext(
            user_input="How are you?",
            conversation_history=messages,
            prompt_version="v1.0",
            system_prompt="Be helpful",
        )
        
        assert len(context.conversation_history) == 2
        assert context.conversation_history[0].role == "user"
        assert context.conversation_history[1].role == "assistant"

    def test_complete_workflow(self) -> None:
        # Create conversation
        conversation = Conversation()
        
        # Add user message
        user_message = Message(content="What is AI?", role="user")
        conversation.add_message(user_message)
        
        # Create prompt context
        context = PromptContext(
            user_input="What is AI?",
            conversation_history=conversation.messages,
            prompt_version="v1.0",
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
            prompt_version="v1.0",
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])