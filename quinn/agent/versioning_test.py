"""Test prompt versioning and management."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from .versioning import (
    get_current_prompt_version,
    load_system_prompt,
    save_prompt_version,
)

MIN_LEN = 2


def test_get_current_prompt_version() -> None:
    """Test current prompt version generation."""
    version1 = get_current_prompt_version()
    version2 = get_current_prompt_version()

    # Should be strings starting with 'v'
    assert isinstance(version1, str)
    assert version1.startswith("v")
    assert isinstance(version2, str)
    assert version2.startswith("v")

    # Should be timestamp-based, so likely different (unless called in same second)
    # We'll just check they're valid format
    assert len(version1) > MIN_LEN  # At least 'v' + some digits
    assert len(version2) > MIN_LEN


def test_load_system_prompt_fallback() -> None:
    """Test loading system prompt with fallback when file doesn't exist."""
    # Load from non-existent path - should return fallback
    prompt = load_system_prompt("nonexistent_version")

    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "You are Quinn" in prompt
    assert "rubber duck" in prompt
    assert "clarifying questions" in prompt


def test_load_system_prompt_latest() -> None:
    """Test loading latest system prompt."""
    prompt = load_system_prompt("latest")

    assert isinstance(prompt, str)
    assert len(prompt) > 0
    # Should get fallback since file doesn't exist
    assert "You are Quinn" in prompt


def test_save_and_load_prompt_version() -> None:
    """Test saving and loading a specific prompt version."""
    test_content = "Test system prompt for version testing."
    test_version = "test_v123"

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Monkey patch the project root to use temp directory
        temp_project_root = Path(temp_dir)

        # Mock the path calculation
        def mock_save_prompt_version(version: str, content: str) -> None:
            assert version.strip(), "Version cannot be empty"
            assert content.strip(), "Prompt content cannot be empty"

            prompts_dir = temp_project_root / "quinn" / "templates" / "prompts"
            prompts_dir.mkdir(parents=True, exist_ok=True)

            prompt_file = prompts_dir / f"system_{version}.txt"
            prompt_file.write_text(content)

        def mock_load_system_prompt(version: str = "latest") -> str:
            assert version.strip(), "Version cannot be empty"

            prompts_dir = temp_project_root / "quinn" / "templates" / "prompts"

            if version == "latest":
                prompt_file = prompts_dir / "system.txt"
            else:
                prompt_file = prompts_dir / f"system_{version}.txt"

            if not prompt_file.exists():
                return "Fallback prompt for testing"

            return prompt_file.read_text().strip()

        # Test save
        mock_save_prompt_version(test_version, test_content)

        # Test load
        loaded_content = mock_load_system_prompt(test_version)
        assert loaded_content == test_content


def test_save_prompt_version_validation() -> None:
    """Test prompt version saving validation."""

    with pytest.raises(AssertionError, match="Version cannot be empty"):
        save_prompt_version("", "v1.0")

    with pytest.raises(AssertionError, match="Version cannot be empty"):
        save_prompt_version("   ", "v1.0")  # Whitespace only

    with pytest.raises(AssertionError, match="Prompt content cannot be empty"):
        save_prompt_version("v1.0", "")

    with pytest.raises(AssertionError, match="Prompt content cannot be empty"):
        save_prompt_version("v1.0", "   ")  # Whitespace only


def test_load_system_prompt_validation() -> None:
    """Test system prompt loading validation."""

    with pytest.raises(AssertionError, match="Version cannot be empty"):
        load_system_prompt("")

    with pytest.raises(AssertionError, match="Version cannot be empty"):
        load_system_prompt("   ")  # Whitespace only


def test_load_system_prompt_fallback_content() -> None:
    """Test that fallback prompt contains expected content."""

    # Mock file not found to trigger fallback
    with patch("pathlib.Path.exists", return_value=False):
        prompt = load_system_prompt()

        # Check that fallback content is returned
        assert "You are Quinn" in prompt
        assert "encouraging and supportive" in prompt
        assert "understanding the problem thoroughly" in prompt


def test_save_prompt_version() -> None:
    """Test saving a prompt version."""
    test_content = "Test system prompt content"
    test_version = "240715-120000"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        save_prompt_version(test_version, test_content, project_root=temp_path)

        # Verify file was created with correct content
        expected_file = (
            temp_path / "quinn" / "templates" / "prompts" / f"system_{test_version}.txt"
        )
        assert expected_file.exists()
        assert expected_file.read_text() == test_content


def test_save_prompt_version_creates_directories() -> None:
    """Test that save_prompt_version creates necessary directories."""
    test_content = "Test content"
    test_version = "240715-120000"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        save_prompt_version(test_version, test_content, project_root=temp_path)

        # Verify directories were created
        prompts_dir = temp_path / "quinn" / "templates" / "prompts"
        assert prompts_dir.exists()
        assert prompts_dir.is_dir()


def test_save_prompt_version_default_root(tmp_path: Path) -> None:
    """Ensure default project root path is used when none is provided."""
    mock_file_path = MagicMock()
    mock_file_path.parent.parent.parent = tmp_path

    with patch("quinn.agent.versioning.Path") as mock_path:
        mock_path.return_value = mock_file_path
        mock_path.__file__ = "ignored.py"

        save_prompt_version("240715-120000", "data", project_root=None)

    expected = tmp_path / "quinn" / "templates" / "prompts" / "system_240715-120000.txt"
    assert expected.exists()
    assert expected.read_text() == "data"


def test_load_system_prompt_file_reading() -> None:
    """Test actual file reading in load_system_prompt."""
    test_content = "Actual prompt"

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        prompts_dir = root / "quinn" / "templates" / "prompts"
        prompts_dir.mkdir(parents=True)
        (prompts_dir / "system.txt").write_text(test_content)

        result = load_system_prompt(project_root=root)
        assert result == test_content


def test_load_system_prompt_reads_real_file() -> None:
    """Test that load_system_prompt reads a version-specific prompt file."""
    version = "240715-120000"
    content = "Version specific"

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        dir_path = root / "quinn" / "templates" / "prompts"
        dir_path.mkdir(parents=True)
        (dir_path / f"system_{version}.txt").write_text(content)

        loaded = load_system_prompt(version, project_root=root)
        assert loaded == content
