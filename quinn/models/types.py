"""Custom type definitions for Quinn AI agent."""

import re
from typing import Annotated

from pydantic import AfterValidator

# Constants for date/time validation
MAX_MONTH = 12
MAX_DAY = 31
MAX_HOUR = 23
MAX_MINUTE = 59
MAX_SECOND = 59


def _validate_date_time_values(date_part: str, time_part: str) -> None:
    """Validate date and time components."""
    _yy, mm, dd = int(date_part[:2]), int(date_part[2:4]), int(date_part[4:6])
    hh, min_val, ss = int(time_part[:2]), int(time_part[2:4]), int(time_part[4:6])
    
    if not (1 <= mm <= MAX_MONTH):
        msg = f"Invalid month in prompt version: {mm}"
        raise ValueError(msg)
    if not (1 <= dd <= MAX_DAY):
        msg = f"Invalid day in prompt version: {dd}"
        raise ValueError(msg)
    if not (0 <= hh <= MAX_HOUR):
        msg = f"Invalid hour in prompt version: {hh}"
        raise ValueError(msg)
    if not (0 <= min_val <= MAX_MINUTE):
        msg = f"Invalid minute in prompt version: {min_val}"
        raise ValueError(msg)
    if not (0 <= ss <= MAX_SECOND):
        msg = f"Invalid second in prompt version: {ss}"
        raise ValueError(msg)


def validate_prompt_version(v: str) -> str:
    """Validate prompt version follows YYMMDD-HHMMSS format."""
    if not v.strip():
        msg = "Prompt version cannot be empty"
        raise ValueError(msg)
    
    # Pattern for YYMMDD-HHMMSS format
    pattern = r"^\d{6}-\d{6}$"
    if not re.match(pattern, v):
        msg = f"Prompt version must follow YYMMDD-HHMMSS format, got: {v}"
        raise ValueError(msg)
    
    # Additional validation for reasonable date/time values
    date_part = v[:6]
    time_part = v[7:]
    _validate_date_time_values(date_part, time_part)
    
    return v


PROMPT_VERSION = Annotated[str, AfterValidator(validate_prompt_version)]


if __name__ == "__main__":
    # Demonstrate prompt version validation
    print("Prompt version validation demonstration:")
    
    # Valid formats
    valid_versions = [
        "240715-120000",
        "231201-235959",
        "250101-000000",
        "241231-143022"
    ]
    
    print("Valid prompt versions:")
    for version in valid_versions:
        try:
            validated = validate_prompt_version(version)
            print(f"  ✓ {version} -> {validated}")
        except ValueError as e:
            print(f"  ✗ {version} -> {e}")
    
    # Invalid formats
    invalid_versions = [
        "",
        "   ",
        "240715",
        "24-07-15-12:00:00", 
        "240715-1200",
        "240715120000",
        "241315-120000",  # Invalid month
        "240732-120000",  # Invalid day
        "240715-250000",  # Invalid hour
        "240715-126000",  # Invalid minute
        "240715-120060",  # Invalid second
    ]
    
    print("\nInvalid prompt versions:")
    for version in invalid_versions:
        try:
            validated = validate_prompt_version(version)
            print(f"  ✓ {version} -> {validated} (unexpected)")
        except ValueError as e:
            print(f"  ✗ {version} -> {e}")
    
    # Test with PROMPT_VERSION type
    from pydantic import BaseModel
    
    class TestModel(BaseModel):
        version: PROMPT_VERSION
    
    print("\nTesting with Pydantic model:")
    try:
        model = TestModel(version="240715-120000")
        print(f"  ✓ Valid model: {model.version}")
    except ValueError as e:
        print(f"  ✗ Model validation error: {e}")
    
    try:
        model = TestModel(version="invalid-format")
        print(f"  ✓ Invalid model (unexpected): {model.version}")
    except ValueError as e:
        print(f"  ✗ Model validation error: {e}")
    
    print("Prompt version validation demonstration completed.")
