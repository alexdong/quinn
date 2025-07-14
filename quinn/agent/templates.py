"""Template handling for Quinn prompts."""

from pathlib import Path

import jinja2

from quinn.models.conversation import Conversation
from quinn.models.message import Message


class PromptTemplateHandler:
    """Handle Jinja2 template rendering for Quinn prompts."""

    def __init__(self) -> None:
        """Initialize template handler with templates directory."""
        templates_dir = Path(__file__).parent.parent / "templates" / "prompts"
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _load_guidance(self) -> str:
        """Load the guidance content from guidance.txt."""
        guidance_path = (
            Path(__file__).parent.parent / "templates" / "prompts" / "guidance.txt"
        )
        assert guidance_path.exists(), "Guidance file not found"
        return guidance_path.read_text(encoding="utf-8").strip()

    def _format_conversation_history(self, conversation: Conversation) -> str:
        """Format conversation history for template rendering."""
        if not conversation.messages:
            return ""

        history_parts = []
        for msg in conversation.messages:
            if msg.user_content:
                history_parts.append(f"User: {msg.user_content}")
            if msg.assistant_content:
                history_parts.append(f"Assistant: {msg.assistant_content}")

        return "\n".join(history_parts)

    def render_initial_prompt(self, user_problem: str) -> str:
        """Render initial prompt template with user problem."""
        assert user_problem.strip(), "User problem cannot be empty"

        template = self.env.get_template("initial_prompt.j2")
        return template.render(
            guidance=self._load_guidance(),
            user_problem=user_problem,
        )

    def render_subsequent_prompt(self, conversation: Conversation) -> str:
        """Render subsequent prompt template with conversation history."""
        assert conversation.messages, "Conversation must have messages"

        conversation_history = self._format_conversation_history(conversation)

        template = self.env.get_template("subsequent_prompt.j2")
        return template.render(
            guidance=self._load_guidance(),
            conversation_history=conversation_history,
        )

    def render_template(self, template_name: str, **kwargs: str) -> str:
        """Render any template with provided variables."""
        template = self.env.get_template(template_name)
        return template.render(**kwargs)


# Convenience functions for direct use
def render_initial_prompt(user_problem: str) -> str:
    """Render initial prompt for a new conversation."""
    handler = PromptTemplateHandler()
    return handler.render_initial_prompt(user_problem)


def render_subsequent_prompt(conversation: Conversation) -> str:
    """Render subsequent prompt for ongoing conversation."""
    handler = PromptTemplateHandler()
    return handler.render_subsequent_prompt(conversation)


if __name__ == "__main__":
    """Demonstrate template functionality."""
    print("🎨 Testing Quinn template functionality...")

    # Test initial prompt
    print("\n📝 Testing initial prompt rendering...")
    initial_prompt = render_initial_prompt(
        "I'm trying to decide whether to use microservices or a monolith for my new web application."
    )
    print(f"✅ Initial prompt rendered ({len(initial_prompt)} chars)")
    assert "microservices" in initial_prompt.lower()
    assert "clarifying questions" in initial_prompt.lower()

    # Test subsequent prompt
    print("\n📝 Testing subsequent prompt rendering...")
    from quinn.models.conversation import Conversation
    from quinn.models.message import Message

    conversation = Conversation()
    conversation.add_message(
        Message(
            conversation_id=conversation.id,
            user_content="I need help with architecture decisions.",
            assistant_content="What specific trade-offs are you considering?",
        )
    )
    conversation.add_message(
        Message(
            conversation_id=conversation.id,
            user_content="I'm mainly worried about scalability and team coordination.",
            assistant_content="Can you tell me more about your team size and expected user growth?",
        )
    )

    subsequent_prompt = render_subsequent_prompt(conversation)
    print(f"✅ Subsequent prompt rendered ({len(subsequent_prompt)} chars)")
    assert "scalability" in subsequent_prompt.lower()
    assert "conversation history" in subsequent_prompt.lower()

    # Test template handler directly
    print("\n📝 Testing template handler...")
    handler = PromptTemplateHandler()
    custom_prompt = handler.render_template(
        "initial_prompt.j2",
        guidance="Test guidance content",
        user_problem="Test problem",
    )
    print(f"✅ Custom template rendered ({len(custom_prompt)} chars)")
    assert "Test problem" in custom_prompt

    print("\n✅ All template tests passed!")
