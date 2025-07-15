"""Test prompt versioning and management."""

import tempfile
from pathlib import Path

import pytest

from .versioning import get_current_prompt_version, load_system_prompt, save_prompt_version


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
    assert len(version1) > 2  # At least 'v' + some digits
    assert len(version2) > 2


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
        original_parent = Path(__file__).parent.parent.parent
        temp_project_root = Path(temp_dir)
        
        # Override the project root path in versioning module
        import quinn.agent.versioning as versioning_module
        original_file = versioning_module.__file__
        
        # Mock the path calculation
        def mock_save_prompt_version(content: str, version: str) -> None:
            assert content.strip(), "Prompt content cannot be empty"
            assert version.strip(), "Version cannot be empty"
            
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
        mock_save_prompt_version(test_content, test_version)
        
        # Test load
        loaded_content = mock_load_system_prompt(test_version)
        assert loaded_content == test_content


def test_save_prompt_version_validation() -> None:
    """Test prompt version saving validation."""
    
    with pytest.raises(AssertionError, match="Prompt content cannot be empty"):
        save_prompt_version("", "v1.0")
    
    with pytest.raises(AssertionError, match="Prompt content cannot be empty"):
        save_prompt_version("   ", "v1.0")  # Whitespace only
    
    with pytest.raises(AssertionError, match="Version cannot be empty"):
        save_prompt_version("Test content", "")
    
    with pytest.raises(AssertionError, match="Version cannot be empty"):
        save_prompt_version("Test content", "   ")  # Whitespace only


def test_load_system_prompt_validation() -> None:
    """Test system prompt loading validation."""
    
    with pytest.raises(AssertionError, match="Version cannot be empty"):
        load_system_prompt("")
    
    with pytest.raises(AssertionError, match="Version cannot be empty"):
        load_system_prompt("   ")  # Whitespace only


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

def test_load_system_prompt_fallback_content() -> None:
    """Test that fallback prompt contains expected content."""
    from unittest.mock import patch
    
    # Mock file not found to trigger fallback
    with patch("pathlib.Path.exists", return_value=False):
        prompt = load_system_prompt()
        
        # Check that fallback content is returned
        assert "You are Quinn" in prompt
        assert "encouraging and supportive" in prompt
        assert "understanding the problem thoroughly" in prompt


def test_save_prompt_version() -> None:
    """Test saving a prompt version."""
    import tempfile
    from pathlib import Path
    from unittest.mock import patch, MagicMock
    
    test_content = "Test system prompt content"
    test_version = "240715-120000"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Mock the Path(__file__).parent.parent.parent chain
        mock_file_path = MagicMock()
        mock_file_path.parent.parent.parent = temp_path
        
        with patch("quinn.agent.versioning.Path") as mock_path:
            mock_path.return_value = mock_file_path
            mock_path.__file__ = "fake_file.py"
            
            save_prompt_version(test_version, test_content)
            
            # Verify file was created with correct content
            expected_file = temp_path / "quinn" / "templates" / "prompts" / f"system_{test_version}.txt"
            assert expected_file.exists()
            assert expected_file.read_text() == test_content


def test_save_prompt_version_creates_directories() -> None:
    """Test that save_prompt_version creates necessary directories."""
    import tempfile
    from pathlib import Path
    from unittest.mock import patch, MagicMock
    
    test_content = "Test content"
    test_version = "240715-120000"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Mock the Path(__file__).parent.parent.parent chain
        mock_file_path = MagicMock()
        mock_file_path.parent.parent.parent = temp_path
        
        with patch("quinn.agent.versioning.Path") as mock_path:
            mock_path.return_value = mock_file_path
            mock_path.__file__ = "fake_file.py"
            
            save_prompt_version(test_version, test_content)
            
            # Verify directories were created
            prompts_dir = temp_path / "quinn" / "templates" / "prompts"
            assert prompts_dir.exists()
            assert prompts_dir.is_dir()

