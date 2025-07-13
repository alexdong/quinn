"""Prompt versioning and management."""

import time
from pathlib import Path


def get_current_prompt_version() -> str:
    """Get current prompt version identifier."""
    # For now, use a simple timestamp-based version

    return f"v{int(time.time())}"


def load_system_prompt(version: str = "latest") -> str:
    """Load system prompt by version."""
    assert version.strip(), "Version cannot be empty"

    # Look for prompt files in templates directory
    project_root = Path(__file__).parent.parent.parent
    prompts_dir = project_root / "quinn" / "templates" / "prompts"

    if version == "latest":
        # Load the default system prompt
        prompt_file = prompts_dir / "system.txt"
    else:
        # Load versioned prompt
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


def save_prompt_version(content: str, version: str) -> None:
    """Save a new prompt version."""
    assert content.strip(), "Prompt content cannot be empty"
    assert version.strip(), "Version cannot be empty"

    project_root = Path(__file__).parent.parent.parent
    prompts_dir = project_root / "quinn" / "templates" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    prompt_file = prompts_dir / f"system_{version}.txt"
    prompt_file.write_text(content)
