"""Command-line interface for Quinn prompt iteration."""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

import click
import jinja2
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax

from quinn.agent.core import generate_response
from quinn.db.conversations import Conversations, DbConversation
from quinn.db.database import create_tables
from quinn.db.messages import Messages
from quinn.db.users import Users
from quinn.models.message import Message
from quinn.models.user import User

console = Console()

# Constants
TITLE_MAX_LENGTH = 50


def _setup_database() -> None:
    """Ensure database tables exist and create CLI user if needed."""
    try:
        # Try to create tables, ignore if they already exist
        try:
            create_tables()
        except Exception as e:
            if "already exists" not in str(e):
                raise

        # Ensure CLI user exists
        cli_user_id = "cli-user"
        if not Users.get_by_id(cli_user_id):
            cli_user = User(
                id=cli_user_id,
                name="CLI User",
                email_addresses=["cli@localhost"],
            )
            Users.create(cli_user)

    except Exception as e:
        console.print(f"[red]Database setup failed: {e}[/red]")
        sys.exit(1)


def _read_stdin() -> str:
    """Read user input from stdin (for piped input)."""
    if sys.stdin.isatty():
        # No piped input, prompt user
        return Prompt.ask("Enter your problem or question")
    # Read from pipe
    return sys.stdin.read().strip()


def _read_prompt_file(prompt_file: str) -> str:
    """Read custom prompt template from file."""
    prompt_path = Path(prompt_file)
    if not prompt_path.exists():
        console.print(f"[red]Prompt file not found: {prompt_file}[/red]")
        sys.exit(1)

    try:
        return prompt_path.read_text(encoding="utf-8")
    except Exception as e:
        console.print(f"[red]Error reading prompt file: {e}[/red]")
        sys.exit(1)


def _render_custom_prompt(template_content: str, user_content: str) -> str:
    """Render custom prompt template with user content."""
    try:
        template = jinja2.Template(template_content)
        return template.render(
            user_problem=user_content,
            user_content=user_content,
            # Add other common variables for backward compatibility
            previous_response="",
            conversation_history="",
        )
    except Exception as e:
        console.print(f"[red]Error rendering template: {e}[/red]")
        sys.exit(1)


async def _generate_and_save_response(
    user_content: str, custom_prompt: str | None = None
) -> Message:
    """Generate AI response and save to database."""
    # Create conversation
    conversation_id = str(uuid4())

    # Create user message
    user_message = Message(
        conversation_id=conversation_id,
        user_content=user_content,
        system_prompt=custom_prompt or "",
    )

    try:
        # Generate response
        with console.status("[bold green]Generating response..."):
            response_message = await generate_response(user_message)

        # Save to database
        with console.status("[bold blue]Saving to database..."):
            # Create conversation record
            title = (
                user_content[:TITLE_MAX_LENGTH] + "..."
                if len(user_content) > TITLE_MAX_LENGTH
                else user_content
            )
            db_conversation = DbConversation(
                conversation_id=conversation_id,
                user_id="cli-user",  # Fixed user for CLI usage
                title=title,
            )
            Conversations.create(db_conversation)

            # Save message to database
            Messages.create(response_message, "cli-user")

        return response_message

    except Exception as e:
        console.print(f"[red]Error generating or saving response: {e}[/red]")
        sys.exit(1)


def _display_response(message: Message) -> None:
    """Display response in user-friendly format."""
    console.print()
    console.print(
        Panel(message.user_content, title="[bold blue]Your Input", border_style="blue")
    )

    console.print()
    console.print(
        Panel(
            message.assistant_content,
            title="[bold green]Quinn's Response",
            border_style="green",
        )
    )

    # Display metadata if available
    if message.metadata:
        console.print()
        metadata_text = (
            f"💰 Cost: ${message.metadata.cost_usd:.6f}\n"
            f"🔢 Tokens: {message.metadata.tokens_used:,}\n"
            f"⏱️  Response Time: {message.metadata.response_time_ms}ms\n"
            f"🤖 Model: {message.metadata.model_used}\n"
            f"📋 Conversation ID: {message.conversation_id}"
        )
        console.print(
            Panel(metadata_text, title="[bold yellow]Metadata", border_style="yellow")
        )


@click.command()
@click.option(
    "-p",
    "--prompt-file",
    type=str,
    help="Path to custom prompt template file (supports Jinja2 variables: {{user_problem}}, {{user_content}})",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug output",
)
def main(prompt_file: str | None, *, debug: bool = False) -> None:
    """Quinn CLI for prompt iteration.

    Usage:
        echo "Your problem here" | quinn -p custom_prompt.j2
        quinn -p custom_prompt.j2  # Interactive mode
        quinn  # Use default prompt
    """
    if debug:
        console.print("[dim]Debug mode enabled[/dim]")

    # Setup database
    _setup_database()

    # Get user input
    user_content = _read_stdin()
    if not user_content.strip():
        console.print("[red]Error: No input provided[/red]")
        sys.exit(1)

    # Read custom prompt if specified
    custom_prompt = None
    if prompt_file:
        template_content = _read_prompt_file(prompt_file)
        custom_prompt = _render_custom_prompt(template_content, user_content)

        if debug:
            console.print()
            console.print(
                Panel(
                    Syntax(custom_prompt, "text", theme="monokai"),
                    title="[bold magenta]Rendered Prompt",
                    border_style="magenta",
                )
            )

    # Generate and save response
    response_message = asyncio.run(
        _generate_and_save_response(user_content, custom_prompt)
    )

    # Display results
    _display_response(response_message)


if __name__ == "__main__":
    main()
