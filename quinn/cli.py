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

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from quinn.core.conversation_manager import ConversationManager
from quinn.core.database_manager import DatabaseManager
from quinn.models.conversation import Conversation
from quinn.models.message import Message
from quinn.utils.logging import setup_logging

console = Console()

# Constants
CLI_USER_ID = "cli-user"
TITLE_MAX_LENGTH = 50
TITLE_TRUNCATE_LENGTH = 47


def _parse_debug_modules(mods: str | None) -> list[str] | None:
    """Parse comma-separated debug module names."""
    return [m.strip() for m in mods.split(",") if m.strip()] if mods else None


def _setup_database() -> None:
    """Ensure database tables exist and create CLI user if needed."""
    try:
        DatabaseManager.setup_database()
        DatabaseManager.ensure_cli_user()
    except Exception as e:
        console.print(f"[red]Database setup failed: {e}[/red]")
        sys.exit(1)


def _reset_all() -> None:
    """Remove all conversations and recreate a fresh database."""
    try:
        DatabaseManager.reset_all()
        DatabaseManager.ensure_cli_user()
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


async def _generate_and_save_response(user_content: str, model: str) -> Message:
    """Generate AI response and save to database."""
    try:
        # Generate response
        with console.status("[bold green]Generating response..."):
            response = await ConversationManager.create_new_conversation(
                CLI_USER_ID, user_content, model
            )

        return response.message

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
    conversations = ConversationManager.list_conversations(CLI_USER_ID)

    if not conversations:
        console.print("[yellow]No conversations found.[/yellow]")
        return

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
    return ConversationManager.get_conversation_by_index(CLI_USER_ID, index)


def _get_most_recent_conversation() -> Conversation | None:
    """Get the most recently updated conversation."""
    return ConversationManager.get_most_recent_conversation(CLI_USER_ID)


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


def _validate_model(model: str) -> None:
    """Validate that the model is supported."""
    try:
        ConversationManager.get_model_config(model)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


async def _continue_conversation(
    conversation_id: str, user_input: str, model: str
) -> Message:
    """Continue an existing conversation with new user input."""
    try:
        # Generate response
        with console.status("[bold green]Generating response..."):
            response = await ConversationManager.continue_conversation(
                conversation_id, CLI_USER_ID, user_input, model
            )

        return response.message

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


def _handle_new_conversation(model: str) -> None:
    """Handle starting a new conversation."""
    # Get user input
    user_content = _read_stdin()
    if not user_content.strip():
        console.print("[red]Error: No input provided[/red]")
        sys.exit(1)

    # Generate and save response
    response_message = asyncio.run(_generate_and_save_response(user_content, model))
    _display_response(response_message)


def _get_last_assistant_message(conversation_id: str) -> str | None:
    """Get the last assistant message from a conversation."""
    return ConversationManager.get_last_assistant_message(conversation_id)


def _format_message_for_editor(content: str) -> str:
    """Format message content with line breaks at column 88 and '> ' prefix for each line."""
    # Split content into paragraphs (preserve intentional line breaks)
    paragraphs = content.split("\n")

    formatted_lines = []
    for paragraph in paragraphs:
        if paragraph.strip():
            # Wrap each paragraph at 88 characters, accounting for "> " prefix (86 chars actual)
            wrapped_lines = textwrap.wrap(paragraph, width=86)
            formatted_lines.extend(f"> {line}" for line in wrapped_lines)
        else:
            # Preserve empty lines
            formatted_lines.append("> ")

    return "\n".join(formatted_lines)


def _handle_continue_recent_conversation(
    recent_conversation: Conversation, model: str
) -> None:
    """Handle continuing the most recent conversation."""
    # Get the last assistant message and format it for the editor
    last_assistant_message = _get_last_assistant_message(recent_conversation.id)

    initial_content = ""
    if last_assistant_message:
        initial_content = _format_message_for_editor(last_assistant_message) + "\n\n"

    # Use editor to get continuation input with the formatted last message
    user_content = _read_from_editor(initial_content)
    if not user_content.strip():
        console.print("[red]Error: No input provided[/red]")
        sys.exit(1)

    response_message = asyncio.run(
        _continue_conversation(recent_conversation.id, user_content, model)
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


def _handle_default_behavior(model: str) -> None:
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
    _handle_new_conversation(model)


@click.command(
    epilog=textwrap.dedent(
        """
        Getting started:

        \b
          \bquinn           # Continue or start new
          \bquinn -n        # Start a new conversation
          \bquinn -c        # Continue most recent
          \bquinn -l        # List all conversations
          \bquinn -c 1      # Continue conversation #1
          \bquinn --reset-all   # Reset all

        Example session:

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

        Conversation flow:

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
    default="claude-sonnet-4",
    help="LLM model to use (default: claude-sonnet-4)",
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
    model: str,
    *,
    debug: bool = False,
    debug_modules: str | None = None,
    reset_all: bool = False,
) -> None:
    """Quinn CLI - AI-powered rubber duck for guided problem-solving.

    Quinn helps you think through problems via back-and-forth discussion. All input
    is provided through your $EDITOR (vim, nano, etc).

    Available models: {models}
    """.format(models=", ".join(ConversationManager.get_available_models()))
    level = logging.INFO
    if debug:
        console.print("[dim]Debug mode enabled[/dim]")
        level = logging.DEBUG

    modules = _parse_debug_modules(debug_modules)
    setup_logging(level=level, debug_modules=modules)

    # Validate model early
    _validate_model(model)

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
        (new, lambda: _handle_new_conversation(model)),
    ]
    for condition, action in actions:
        if condition:
            action()
            break
    else:
        _handle_default_behavior(model)


if __name__ == "__main__":
    main()
