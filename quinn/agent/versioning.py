"""Prompt versioning and management."""

from datetime import UTC, datetime
from pathlib import Path

from quinn.models.types import PROMPT_VERSION


def get_current_prompt_version() -> PROMPT_VERSION:
    """Get current prompt version identifier in vYYMMDD-HHMMSS format."""
    now = datetime.now(UTC)
    return f"v{now.strftime('%y%m%d-%H%M%S')}"


def load_system_prompt(version: str | PROMPT_VERSION = "latest") -> str:
    """Load system prompt by version."""
    assert version.strip(), "Version cannot be empty"

    # Look for prompt files in templates directory
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


def save_prompt_version(version: PROMPT_VERSION, content: str) -> None:
    """Save a new prompt version."""
    assert version.strip(), "Version cannot be empty"
    assert content.strip(), "Prompt content cannot be empty"

    project_root = Path(__file__).parent.parent.parent
    prompts_dir = project_root / "quinn" / "templates" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    prompt_file = prompts_dir / f"system_{version}.txt"
    prompt_file.write_text(content)
