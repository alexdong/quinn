"""Template handling for Quinn prompts."""

from pathlib import Path

import jinja2

from quinn.models.conversation import Conversation
from quinn.models.message import Message


class PromptGenerator:
    """Handle Jinja2 template rendering for Quinn prompts."""

    def __init__(self) -> None:
        """Initialize template handler with templates directory."""
        templates_dir = Path(__file__).parent.parent / "templates" / "prompts"
        self.jinja_env = jinja2.Environment(
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
            history_parts.append(f"User: {msg.user_content}")
            history_parts.append(f"Assistant: {msg.assistant_content}")
            history_parts.append("-------\n\n")

        return "\n".join(history_parts)

    def render_initial_prompt(self, user_problem: str) -> str:
        """Render initial prompt template with user problem."""
        assert user_problem.strip(), "User problem cannot be empty"

        template = self.jinja_env.get_template("initial_prompt.j2")
        return template.render(
            guidance=self._load_guidance(),
            user_problem=user_problem,
        )

    def render_subsequent_prompt(self, conversation: Conversation) -> str:
        """Render subsequent prompt template with conversation history."""
        assert conversation.messages, "Conversation must have messages"

        conversation_history = self._format_conversation_history(conversation)

        template = self.jinja_env.get_template("subsequent_prompt.j2")
        return template.render(
            guidance=self._load_guidance(),
            conversation_history=conversation_history,
        )

    def render_template(self, template_name: str, **kwargs: str) -> str:
        """Render any template with provided variables."""
        template = self.jinja_env.get_template(template_name)
        return template.render(**kwargs)


# Convenience functions for direct use
def render_initial_prompt(user_problem: str) -> str:
    """Render initial prompt for a new conversation."""
    handler = PromptGenerator()
    return handler.render_initial_prompt(user_problem)


def render_subsequent_prompt(conversation: Conversation) -> str:
    """Render subsequent prompt for ongoing conversation."""
    handler = PromptGenerator()
    return handler.render_subsequent_prompt(conversation)


if __name__ == "__main__":
    """Demonstrate template functionality."""
    print("🎨 Testing Quinn template functionality...")

    # Test initial prompt
    print("\n📝 Testing initial prompt rendering...")
    user_problem = "I'm trying to decide whether to use fasthtml or flask for my new web application."
    initial_prompt = render_initial_prompt(user_problem)
    print(f"✅ Initial prompt rendered ({len(initial_prompt)} chars)")
    print("\n" + "=" * 50)
    print("INBOUND (User Problem):")
    print("=" * 50)
    print(user_problem)
    print("\n" + "=" * 50)
    print("OUTBOUND (Initial Prompt):")
    print("=" * 50)
    print(initial_prompt)
    print("=" * 50)
    assert "fasthtml" in initial_prompt.lower()
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
    print("\n" + "=" * 50)
    print("INBOUND (Conversation History):")
    print("=" * 50)
    for i, msg in enumerate(conversation.messages, 1):
        print(f"Message {i}:")
        print(f"  User: {msg.user_content}")
        print(f"  Assistant: {msg.assistant_content}")
        print()
    print("\n" + "=" * 50)
    print("OUTBOUND (Subsequent Prompt):")
    print("=" * 50)
    print(subsequent_prompt)
    print("=" * 50)
    assert "scalability" in subsequent_prompt.lower()
    assert "conversation history" in subsequent_prompt.lower()

    # Test template handler directly
    print("\n📝 Testing template handler...")
    handler = PromptGenerator()
    custom_prompt = handler.render_template(
        "initial_prompt.j2",
        guidance="Test guidance content",
        user_problem="Test problem",
    )
    print(f"✅ Custom template rendered ({len(custom_prompt)} chars)")
    assert "Test problem" in custom_prompt

    print("\n✅ All template tests passed!")

    # Calculate costs for all models
    print("\n💰 Calculating template costs for all models...")

    from rich.console import Console
    from rich.table import Table

    from quinn.agent.cost import calculate_cost, get_supported_models
    from quinn.models.config import AgentConfig

    console = Console()

    # Get token counts (rough estimate: 1 token ≈ 4 characters)
    initial_tokens = len(initial_prompt) // 4
    subsequent_tokens = len(subsequent_prompt) // 4

    table = Table(title="Template Cost Analysis by Model (Sorted by Total Cost)")
    table.add_column("Model", style="cyan")
    table.add_column("Initial Cost", style="yellow")
    table.add_column("Subsequent Cost", style="yellow")
    table.add_column("Total Cost", style="red")

    # Get models from config that have pricing data
    config_models = set(AgentConfig.get_all_models())
    pricing_models = set(get_supported_models())
    available_models = config_models.intersection(pricing_models)

    # Calculate costs and store in list for sorting
    cost_data = []
    for model in available_models:
        try:
            # Calculate cost for just input tokens (templates are input only)
            initial_cost = calculate_cost(model, initial_tokens, 0)
            subsequent_cost = calculate_cost(model, subsequent_tokens, 0)
            total_cost = initial_cost + subsequent_cost

            cost_data.append(
                {
                    "model": model,
                    "initial_cost": initial_cost,
                    "subsequent_cost": subsequent_cost,
                    "total_cost": total_cost,
                }
            )
        except Exception as e:
            print(f"⚠️  Could not calculate cost for {model}: {e}")
            continue

    # Sort by total cost ascending
    cost_data.sort(key=lambda x: x["total_cost"])

    # Add rows to table
    for item in cost_data:
        table.add_row(
            item["model"],
            f"${item['initial_cost']:.6f}",
            f"${item['subsequent_cost']:.6f}",
            f"${item['total_cost']:.6f}",
        )

    console.print(table)
    print(
        f"\n📊 Token counts: Initial={initial_tokens:,}, Subsequent={subsequent_tokens:,}"
    )
