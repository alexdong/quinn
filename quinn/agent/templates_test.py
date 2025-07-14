"""Tests for Quinn template functionality."""

import pytest

from quinn.models.conversation import Conversation
from quinn.models.message import Message

from .templates import PromptGenerator, render_initial_prompt, render_subsequent_prompt


class TestPromptGenerator:
    """Test PromptGenerator class."""

    def test_init(self) -> None:
        """Test template handler initialization."""
        handler = PromptGenerator()
        assert handler.jinja_env is not None
        assert handler.jinja_env.loader is not None

    def test_load_guidance(self) -> None:
        """Test guidance loading."""
        handler = PromptGenerator()
        guidance = handler._load_guidance()
        assert isinstance(guidance, str)
        assert len(guidance) > 0
        assert "Core Principles" in guidance

    def test_format_conversation_history_empty(self) -> None:
        """Test conversation history formatting with empty conversation."""
        handler = PromptGenerator()
        conversation = Conversation()
        history = handler._format_conversation_history(conversation)
        assert history == ""

    def test_format_conversation_history_with_messages(self) -> None:
        """Test conversation history formatting with messages."""
        handler = PromptGenerator()
        conversation = Conversation()

        # Add user message
        user_message = Message(
            conversation_id=conversation.id,
            user_content="What should I do?",
        )
        conversation.add_message(user_message)

        # Add assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            user_content="What should I do?",
            assistant_content="What specific problem are you facing?",
        )
        conversation.add_message(assistant_message)

        history = handler._format_conversation_history(conversation)
        assert "User: What should I do?" in history
        assert "Assistant: What specific problem are you facing?" in history

    def test_render_initial_prompt(self) -> None:
        """Test initial prompt rendering."""
        handler = PromptGenerator()
        user_problem = "I can't decide between React and Vue for my project."

        prompt = handler.render_initial_prompt(user_problem)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert user_problem in prompt
        assert "Core Principles" in prompt
        assert "clarifying questions" in prompt.lower()

    def test_render_initial_prompt_empty_problem(self) -> None:
        """Test initial prompt rendering fails with empty problem."""
        handler = PromptGenerator()
        with pytest.raises(AssertionError, match="User problem cannot be empty"):
            handler.render_initial_prompt("")

    def test_render_initial_prompt_whitespace_problem(self) -> None:
        """Test initial prompt rendering fails with whitespace-only problem."""
        handler = PromptGenerator()
        with pytest.raises(AssertionError, match="User problem cannot be empty"):
            handler.render_initial_prompt("   ")

    def test_render_subsequent_prompt(self) -> None:
        """Test subsequent prompt rendering."""
        handler = PromptGenerator()
        conversation = Conversation()

        # Add initial message
        initial_message = Message(
            conversation_id=conversation.id,
            user_content="I need help with database design.",
            assistant_content="What type of data will you be storing?",
        )
        conversation.add_message(initial_message)

        prompt = handler.render_subsequent_prompt(conversation)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "database design" in prompt.lower()
        assert "conversation history" in prompt.lower()
        assert "Core Principles" in prompt

    def test_render_subsequent_prompt_empty_conversation(self) -> None:
        """Test subsequent prompt rendering fails with empty conversation."""
        handler = PromptGenerator()
        conversation = Conversation()

        with pytest.raises(AssertionError, match="Conversation must have messages"):
            handler.render_subsequent_prompt(conversation)

    def test_render_template_generic(self) -> None:
        """Test generic template rendering."""
        handler = PromptGenerator()

        # Test with initial_prompt.j2
        result = handler.render_template(
            "initial_prompt.j2",
            guidance="Test guidance content",
            user_problem="Test problem statement",
        )
        assert "Test guidance content" in result
        assert "Test problem statement" in result


class TestConvenienceFunctions:
    """Test convenience functions for template rendering."""

    def test_render_initial_prompt_function(self) -> None:
        """Test render_initial_prompt convenience function."""
        user_problem = "Should I use Docker or Kubernetes for deployment?"

        prompt = render_initial_prompt(user_problem)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert user_problem in prompt
        assert "Core Principles" in prompt

    def test_render_subsequent_prompt_function(self) -> None:
        """Test render_subsequent_prompt convenience function."""
        conversation = Conversation()
        conversation.add_message(
            Message(
                conversation_id=conversation.id,
                user_content="I'm learning Python.",
                assistant_content="What aspects of Python interest you most?",
            )
        )

        prompt = render_subsequent_prompt(conversation)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Python" in prompt
        assert "Core Principles" in prompt


class TestTemplateIntegration:
    """Test template integration with conversation flow."""

    def test_full_conversation_flow(self) -> None:
        """Test complete conversation flow with templates."""
        # Start new conversation
        initial_problem = "I'm starting a new startup and need to choose a tech stack."
        initial_prompt = render_initial_prompt(initial_problem)

        assert initial_problem in initial_prompt
        assert "clarifying questions" in initial_prompt.lower()

        # Create conversation and add initial exchange
        conversation = Conversation()
        conversation.add_message(
            Message(
                conversation_id=conversation.id,
                user_content=initial_problem,
                assistant_content="What kind of product are you building? What's your team's experience level?",
            )
        )

        # Continue conversation - add user response to conversation
        conversation.add_message(
            Message(
                conversation_id=conversation.id,
                user_content="We're building a social media platform. Team has mostly frontend experience.",
                assistant_content="What specific challenges do you anticipate with backend complexity?",
            )
        )

        subsequent_prompt = render_subsequent_prompt(conversation)

        assert "social media platform" in subsequent_prompt.lower()
        assert "conversation history" in subsequent_prompt.lower()
        assert initial_problem in subsequent_prompt
        assert "Core Principles" in subsequent_prompt

    def test_multiple_exchanges(self) -> None:
        """Test handling multiple conversation exchanges."""
        conversation = Conversation()

        # Add multiple message pairs
        messages_data = [
            (
                "What programming language should I learn?",
                "What are your goals with programming?",
            ),
            (
                "I want to build mobile apps.",
                "Have you considered cross-platform vs native development?",
            ),
            (
                "I think cross-platform makes more sense.",
                "What factors led you to that conclusion?",
            ),
        ]

        for user_content, assistant_content in messages_data:
            conversation.add_message(
                Message(
                    conversation_id=conversation.id,
                    user_content=user_content,
                    assistant_content=assistant_content,
                )
            )

        # Add final exchange
        conversation.add_message(
            Message(
                conversation_id=conversation.id,
                user_content="Faster development time and code reuse across platforms.",
                assistant_content="What framework are you considering for cross-platform development?",
            )
        )

        prompt = render_subsequent_prompt(conversation)

        # Check that all previous exchanges are preserved
        assert "programming language" in prompt.lower()
        assert "mobile apps" in prompt.lower()
        assert "cross-platform" in prompt.lower()
        assert "Faster development time" in prompt
        assert "Core Principles" in prompt
