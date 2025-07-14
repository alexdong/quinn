"""Tests for custom type definitions and validation."""

import pytest

from .types import validate_prompt_version


def test_validate_prompt_version_valid_format() -> None:
    """Test validate_prompt_version with valid format."""
    valid_version = "240315-142530"
    result = validate_prompt_version(valid_version)
    assert result == valid_version


def test_validate_prompt_version_empty_string() -> None:
    """Test validate_prompt_version with empty string."""
    with pytest.raises(ValueError, match="Prompt version cannot be empty"):
        validate_prompt_version("")
    
    with pytest.raises(ValueError, match="Prompt version cannot be empty"):
        validate_prompt_version("   ")


def test_validate_prompt_version_invalid_format() -> None:
    """Test validate_prompt_version with invalid format."""
    with pytest.raises(ValueError, match="Prompt version must follow YYMMDD-HHMMSS format"):
        validate_prompt_version("24-03-15")
    
    with pytest.raises(ValueError, match="Prompt version must follow YYMMDD-HHMMSS format"):
        validate_prompt_version("240315")
    
    with pytest.raises(ValueError, match="Prompt version must follow YYMMDD-HHMMSS format"):
        validate_prompt_version("240315-1425")
    
    with pytest.raises(ValueError, match="Prompt version must follow YYMMDD-HHMMSS format"):
        validate_prompt_version("240315142530")


def test_validate_prompt_version_invalid_month() -> None:
    """Test validate_prompt_version with invalid month."""
    with pytest.raises(ValueError, match="Invalid month in prompt version"):
        validate_prompt_version("241315-142530")  # Month 13
    
    with pytest.raises(ValueError, match="Invalid month in prompt version"):
        validate_prompt_version("240015-142530")  # Month 0


def test_validate_prompt_version_invalid_day() -> None:
    """Test validate_prompt_version with invalid day."""
    with pytest.raises(ValueError, match="Invalid day in prompt version"):
        validate_prompt_version("240332-142530")  # Day 32
    
    with pytest.raises(ValueError, match="Invalid day in prompt version"):
        validate_prompt_version("240300-142530")  # Day 0


def test_validate_prompt_version_invalid_hour() -> None:
    """Test validate_prompt_version with invalid hour."""
    with pytest.raises(ValueError, match="Invalid hour in prompt version"):
        validate_prompt_version("240315-242530")  # Hour 24
    
    with pytest.raises(ValueError, match="Invalid hour in prompt version"):
        validate_prompt_version("240315-992530")  # Hour 99


def test_validate_prompt_version_invalid_minute() -> None:
    """Test validate_prompt_version with invalid minute."""
    with pytest.raises(ValueError, match="Invalid minute in prompt version"):
        validate_prompt_version("240315-146030")  # Minute 60
    
    with pytest.raises(ValueError, match="Invalid minute in prompt version"):
        validate_prompt_version("240315-149930")  # Minute 99


def test_validate_prompt_version_invalid_second() -> None:
    """Test validate_prompt_version with invalid second."""
    with pytest.raises(ValueError, match="Invalid second in prompt version"):
        validate_prompt_version("240315-142560")  # Second 60
    
    with pytest.raises(ValueError, match="Invalid second in prompt version"):
        validate_prompt_version("240315-142599")  # Second 99


def test_validate_prompt_version_boundary_values() -> None:
    """Test validate_prompt_version with boundary values."""
    # Valid boundary values
    assert validate_prompt_version("240101-000000") == "240101-000000"  # Min values
    assert validate_prompt_version("241231-235959") == "241231-235959"  # Max values
    assert validate_prompt_version("240229-120000") == "240229-120000"  # Leap year day
    
    # Test other valid dates
    assert validate_prompt_version("240630-235959") == "240630-235959"  # June 30
    assert validate_prompt_version("240731-000000") == "240731-000000"  # July 31


if __name__ == "__main__":
    pytest.main([__file__, "-v"])