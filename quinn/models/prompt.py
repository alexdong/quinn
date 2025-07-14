"""Prompt context data models."""

import uuid
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

from .types import PROMPT_VERSION

if TYPE_CHECKING:
    from .conversation import Message


class PromptContext(BaseModel):
    """Context passed to AI agent for response generation."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_input: str = ""
    conversation_history: list["Message"] = Field(default_factory=list)
    prompt_version: PROMPT_VERSION = ""
    system_prompt: str = ""

    @field_validator("user_input", "system_prompt")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate string fields are not empty."""
        if not v.strip():
            msg = "Field cannot be empty"
            raise ValueError(msg)
        return v
