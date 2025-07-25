"""Prompt versioning and management."""

from datetime import UTC, datetime
from pathlib import Path

from quinn.models.types import PROMPT_VERSION


def get_current_prompt_version() -> PROMPT_VERSION:
    """Get current prompt version identifier in vYYMMDD-HHMMSS format."""
    now = datetime.now(UTC)
    return f"v{now.strftime('%y%m%d-%H%M%S')}"


def load_system_prompt(
    version: str | PROMPT_VERSION = "latest",
    project_root: Path | None = None,
) -> str:
    """Load system prompt by version.

    Parameters
    ----------
    version:
        The prompt version identifier. ``"latest"`` loads the default prompt.
    project_root:
        Optional base directory for locating the prompt files. When ``None`` the
        path is derived from ``__file__`` which points to the installed
        location of the package. This parameter exists primarily for testing and
        does not change the public behaviour of the function.
    """
    assert version.strip(), "Version cannot be empty"

    # Look for prompt files in templates directory
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent
    prompts_dir = project_root / "quinn" / "templates" / "prompts"

    if version == "latest":
        # Load the default system prompt
        prompt_file = prompts_dir / "system.txt"
    else:
        # Load versioned prompt - version is already validated if it's PROMPT_VERSION type
        prompt_file = prompts_dir / f"system_{version}.txt"

    if not prompt_file.exists():
        # Fallback to basic prompt
        return """You are Quinn, an AI rubber duck that helps users solve problems through guided questions.

Your role is to ask clarifying questions that help users think through their problems, NOT to provide direct solutions.

Key principles:
- Ask open-ended questions that promote self-discovery
- Never provide direct answers or solutions
- Guide users to find their own solutions through structured thinking
- Be encouraging and supportive
- Focus on understanding the problem thoroughly before exploring solutions"""

    return prompt_file.read_text().strip()


def save_prompt_version(
    version: PROMPT_VERSION,
    content: str,
    project_root: Path | None = None,
) -> None:
    """Save a new prompt version.

    This helper writes ``content`` to a versioned prompt file. ``project_root``
    mirrors the argument of :func:`load_system_prompt` and allows tests to
    operate without touching the real filesystem.
    """
    assert version.strip(), "Version cannot be empty"
    assert content.strip(), "Prompt content cannot be empty"

    if project_root is None:
        project_root = Path(__file__).parent.parent.parent
    prompts_dir = project_root / "quinn" / "templates" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    prompt_file = prompts_dir / f"system_{version}.txt"
    prompt_file.write_text(content)
