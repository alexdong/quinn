"""Command-line interface for Quinn prompt iteration."""

import asyncio
import logging
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import cast
from uuid import uuid4

import click
import jinja2
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table

from quinn.agent.core import generate_response
from quinn.db.conversations import ConversationStore
from quinn.db.database import DATABASE_FILE, create_tables
from quinn.db.messages import MessageStore
from quinn.db.users import UserStore
from quinn.models.config import AgentConfig
from quinn.models.conversation import Conversation
from quinn.models.message import Message
from quinn.models.user import User
from quinn.utils.logging import setup_logging

console = Console()

# Constants
TITLE_MAX_LENGTH = 50
TITLE_TRUNCATE_LENGTH = 47


def _create_tables_if_needed() -> None:
    """Create database tables if they don't exist."""
    try:
        create_tables()
    except Exception as e:
        # Silently ignore if tables already exist
        if "already exists" not in str(e):
            raise


def _create_cli_user_if_needed() -> None:
    """Create CLI user if it doesn't exist."""
    cli_user_id = "cli-user"
    try:
        if not UserStore.get_by_id(cli_user_id):
            cli_user = User(
                id=cli_user_id,
                name="CLI User",
                email_addresses=["cli@localhost"],
            )
            UserStore.create(cli_user)
    except Exception as e:
        # Silently ignore if user already exists
        if "already exists" not in str(e):
            raise


def _parse_debug_modules(mods: str | None) -> list[str] | None:
    """Parse comma-separated debug module names."""
    return [m.strip() for m in mods.split(",") if m.strip()] if mods else None


def _setup_database() -> None:
    """Ensure database tables exist and create CLI user if needed."""
    try:
        _create_tables_if_needed()
        _create_cli_user_if_needed()
    except Exception as e:
        console.print(f"[red]Database setup failed: {e}[/red]")
        sys.exit(1)


def _reset_all() -> None:
    """Remove all conversations and recreate a fresh database."""
    try:
        Path(DATABASE_FILE).unlink(missing_ok=True)
        _setup_database()
        console.print("[green]All conversations reset.[/green]")
    except Exception as e:  # pragma: no cover - rare failure
        console.print(f"[red]Failed to reset conversations: {e}[/red]")
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
    user_content: str, custom_prompt: str | None = None, model: str = "gemini-2.5-flash"
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

    config = _get_model_config(model)

    try:
        # Generate response
        with console.status("[bold green]Generating response..."):
            response_message = await generate_response(user_message, config=config)

        # Save to database
        with console.status("[bold blue]Saving to database..."):
            # Create conversation record
            title = (
                user_content[:TITLE_MAX_LENGTH] + "..."
                if len(user_content) > TITLE_MAX_LENGTH
                else user_content
            )
            db_conversation = Conversation(
                id=conversation_id,
                user_id="cli-user",  # Fixed user for CLI usage
                title=title,
            )
            ConversationStore.create(db_conversation)

            # Save message to database
            MessageStore.create(response_message, "cli-user")

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


def _list_conversations() -> None:
    """List all conversations for the CLI user."""
    conversations = ConversationStore.get_by_user("cli-user")

    if not conversations:
        console.print("[yellow]No conversations found.[/yellow]")
        return

    # Sort by updated_at descending (most recent first)
    conversations.sort(key=lambda x: x.updated_at, reverse=True)

    table = Table(title="Conversations")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Messages", justify="right", style="green")
    table.add_column("Total Cost", justify="right", style="yellow")
    table.add_column("Status", style="blue")
    table.add_column("Updated", style="dim")

    for i, conv in enumerate(conversations, 1):
        # Use 1-based indexing for user-friendly display
        title = conv.title or "Untitled"
        if len(title) > TITLE_MAX_LENGTH:
            title = title[:TITLE_TRUNCATE_LENGTH] + "..."

        table.add_row(
            str(i),
            title,
            str(conv.message_count),
            f"${conv.total_cost:.6f}",
            conv.status,
            conv.updated_at.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


def _get_conversation_by_index(index: int) -> Conversation | None:
    """Get conversation by 1-based index (as shown in list)."""
    conversations = ConversationStore.get_by_user("cli-user")
    if not conversations:
        return None

    # Sort by updated_at descending (most recent first)
    conversations.sort(key=lambda x: x.updated_at, reverse=True)

    if index < 1 or index > len(conversations):
        return None

    return conversations[index - 1]  # Convert to 0-based index


def _get_most_recent_conversation() -> Conversation | None:
    """Get the most recently updated conversation."""
    conversations = ConversationStore.get_by_user("cli-user")
    if not conversations:
        return None

    # Sort by updated_at descending and return the first one
    conversations.sort(key=lambda x: x.updated_at, reverse=True)
    return conversations[0]


def _read_from_editor(initial_content: str = "") -> str:
    """Open editor to get user input."""
    editor = os.environ.get("EDITOR", "vim")

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
        f.write(initial_content)
        f.flush()
        temp_file = f.name

    try:
        subprocess.run([editor, temp_file], check=True)

        with Path(temp_file).open() as f:
            return f.read().strip()

    finally:
        Path(temp_file).unlink()


def _get_model_config(model: str) -> AgentConfig:
    """Get the model configuration for the given model name."""
    model_configs = {
        "gemini-2.5-flash": AgentConfig.gemini25flash,
        "gemini-2.5-flash-thinking": AgentConfig.gemini25flashthinking,
        "claude-4-sonnet": AgentConfig.sonnet4,
        "gpt-4o-mini": AgentConfig.o4mini,
        "gpt-4.1": AgentConfig.gpt41,
        "gpt-4.1-mini": AgentConfig.gpt41mini,
    }

    if model not in model_configs:
        console.print(
            f"[red]Error: Unsupported model '{model}'. Available models: {', '.join(model_configs.keys())}[/red]"
        )
        sys.exit(1)

    return model_configs[model]()


def _build_conversation_context(conversation_id: str, user_input: str) -> str:
    """Build conversation context with previous messages."""
    # Get existing messages to build conversation history
    existing_messages = MessageStore.get_by_conversation(conversation_id)

    # Build conversation history for context
    conversation_history = []
    for msg in existing_messages:
        conversation_history.append(f"User: {msg.user_content}")
        conversation_history.append(f"Quinn: {msg.assistant_content}")

    # Add conversation history as context
    if conversation_history:
        context = "\n\n".join(conversation_history)
        return f"Previous conversation:\n{context}\n\nNew message: {user_input}"

    return user_input


async def _continue_conversation(
    conversation_id: str, user_input: str, model: str
) -> Message:
    """Continue an existing conversation with new user input."""
    # Create new user message with context
    user_message = Message(
        conversation_id=conversation_id,
        user_content=_build_conversation_context(conversation_id, user_input),
        system_prompt="",  # Use default system prompt
    )

    config = _get_model_config(model)

    try:
        # Generate response
        with console.status("[bold green]Generating response..."):
            response_message = await generate_response(user_message, config=config)

        # Update conversation message count and cost
        conversation = ConversationStore.get_by_id(conversation_id)
        if conversation:
            conversation.message_count += 1
            if response_message.metadata:
                conversation.total_cost += response_message.metadata.cost_usd
            ConversationStore.update(conversation)

        # Save message to database
        with console.status("[bold blue]Saving to database..."):
            MessageStore.create(response_message, "cli-user")

        return response_message

    except Exception as e:
        console.print(f"[red]Error generating or saving response: {e}[/red]")
        sys.exit(1)


def _handle_continue_conversation(continue_id: int, model: str) -> None:
    """Handle continuing a specific conversation."""
    conversation = _get_conversation_by_index(continue_id)
    if not conversation:
        console.print(f"[red]Error: Conversation {continue_id} not found[/red]")
        sys.exit(1)
    assert conversation is not None

    # Get user input for continuation
    user_content = _read_stdin()
    if not user_content.strip():
        console.print("[red]Error: No input provided[/red]")
        sys.exit(1)

    # Continue the conversation
    response_message = asyncio.run(
        _continue_conversation(conversation.id, user_content, model)
    )
    _display_response(response_message)


def _handle_new_conversation(
    prompt_file: str | None, model: str, *, debug: bool = False
) -> None:
    """Handle starting a new conversation."""
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
        _generate_and_save_response(user_content, custom_prompt, model)
    )
    _display_response(response_message)


def _handle_continue_recent_conversation(
    recent_conversation: Conversation, model: str
) -> None:
    """Handle continuing the most recent conversation."""
    # Use editor to get continuation input
    user_content = _read_from_editor()
    if not user_content.strip():
        console.print("[red]Error: No input provided[/red]")
        sys.exit(1)

    response_message = asyncio.run(
        _continue_conversation(recent_conversation.id, user_content, model)
    )
    _display_response(response_message)


def _handle_new_conversation_with_content(
    user_content: str, prompt_file: str | None, model: str, *, debug: bool = False
) -> None:
    """Handle creating a new conversation with the provided content."""
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
        _generate_and_save_response(user_content, custom_prompt, model)
    )
    _display_response(response_message)


def _get_user_input_for_new_conversation() -> str:
    """Get user input for a new conversation, either from editor or pipe."""
    if sys.stdin.isatty():
        # Start new conversation using editor
        user_content = _read_from_editor()
        if not user_content.strip():
            console.print("[red]Error: No input provided[/red]")
            sys.exit(1)
        return user_content
    # Read from pipe - start new conversation
    user_content = sys.stdin.read().strip()
    if not user_content:
        console.print("[red]Error: No input provided[/red]")
        sys.exit(1)
    return user_content


def _handle_default_behavior(
    prompt_file: str | None, model: str, *, debug: bool = False
) -> None:
    """Handle default behavior: start new conversation or resume most recent."""
    if sys.stdin.isatty():
        # No piped input, check for most recent conversation
        recent_conversation = _get_most_recent_conversation()
        if recent_conversation:
            # Ask if user wants to continue or start new
            choice = Prompt.ask(
                f"Continue most recent conversation '{recent_conversation.title}'?",
                choices=["y", "n"],
                default="y",
            )
            if choice.lower() == "y":
                _handle_continue_recent_conversation(recent_conversation, model)
                return

    # Get user input for new conversation
    user_content = _get_user_input_for_new_conversation()
    _handle_new_conversation_with_content(user_content, prompt_file, model, debug=debug)


@click.command(
    epilog=textwrap.dedent(
        """
        GETTING STARTED:

        \b
          \bquinn           # Continue or start new
          \bquinn -n        # Start a new conversation
          \bquinn -c        # Continue most recent
          \bquinn -l        # List all conversations
          \bquinn -c 1      # Continue conversation #1
          \bquinn --reset-all   # Reset all

        EXAMPLE SESSION:

        \b
          \b$ quinn
          \b# Opens $EDITOR since no previous conversation
          \b# Type your problem

          \b# Quinn responds with clarifying questions

          \b$ quinn
          \b# Opens $EDITOR to continue
          \b# Answer the clarifying questions

          \b$ quinn
          \b# Continue until you reach a solution

        CONVERSATION FLOW:

        \b
          \b1. Describe your problem or challenge
          \b2. Quinn asks clarifying questions
          \b3. Provide more details and constraints
          \b4. Quinn guides you through solutions
          \b5. Continue iterating until clarity

        TIPS:

        \b
          \b- Set EDITOR: export EDITOR=vim
          \b- Conversations saved locally in SQLite
          \b- Use 'quinn -l' to see history
          \b- Each conversation maintains context
        """
    )
)
@click.option(
    "-n",
    "--new",
    is_flag=True,
    help="Start a new conversation",
)
@click.option(
    "-l",
    "--list",
    "list_conversations",
    is_flag=True,
    help="List all conversations",
)
@click.option(
    "-c",
    "--continue",
    "continue_id",
    type=int,
    help="Continue conversation with ID N",
)
@click.option(
    "-m",
    "--model",
    type=str,
    default="claude-4-sonnet",
    help="LLM model to use (default: claude-4-sonnet)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug output",
)
@click.option(
    "--debug-modules",
    type=str,
    help="Comma-separated modules for debug logging",
)
@click.option(
    "--reset-all",
    is_flag=True,
    help="Delete all conversations and start fresh",
)
def main(
    new: bool,  # noqa: FBT001
    list_conversations: bool,  # noqa: FBT001
    continue_id: int | None,
    prompt_file: str | None,
    model: str,
    *,
    debug: bool = False,
    debug_modules: str | None = None,
    reset_all: bool = False,
) -> None:
    """Quinn CLI - AI-powered rubber duck for guided problem-solving.

    Quinn helps you think through problems via back-and-forth discussion. All input
    is provided through your $EDITOR (vim, nano, etc).

    Available models: claude-4-sonnet (default), gemini-2.5-flash, gemini-2.5-flash-thinking,
    gpt-4o-mini, gpt-4.1, gpt-4.1-mini
    """
    level = logging.INFO
    if debug:
        console.print("[dim]Debug mode enabled[/dim]")
        level = logging.DEBUG

    modules = _parse_debug_modules(debug_modules)
    setup_logging(level=level, debug_modules=modules)

    # Setup database or reset if requested
    if reset_all:
        _reset_all()
        return

    _setup_database()

    actions = [
        (list_conversations, lambda: _list_conversations()),
        (
            continue_id is not None,
            lambda: _handle_continue_conversation(cast("int", continue_id), model),
        ),
        (new, lambda: _handle_new_conversation(prompt_file, model, debug=debug)),
    ]
    for condition, action in actions:
        if condition:
            action()
            break
    else:
        _handle_default_behavior(prompt_file, model, debug=debug)


if __name__ == "__main__":
    main()
