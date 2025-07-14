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
