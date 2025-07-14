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


if __name__ == "__main__":
    # Demonstrate PromptContext usage
    print("PromptContext demonstration:")
    
    # Create messages for history
    from .conversation import Message
    
    history = [
        Message(content="What is AI?", role="user"),
        Message(content="AI stands for Artificial Intelligence...", role="assistant"),
        Message(content="How does machine learning work?", role="user"),
    ]
    
    # Basic prompt context
    basic_context = PromptContext(
        user_input="Explain neural networks",
        prompt_version="240715-120000",
        system_prompt="You are a helpful AI assistant specializing in technology."
    )
    print(f"Basic context: {basic_context.user_input}")
    print(f"Prompt version: {basic_context.prompt_version}")
    print(f"Context ID: {basic_context.id[:8]}...")
    
    # Context with conversation history
    context_with_history = PromptContext(
        user_input="Can you give me a simple example?",
        conversation_history=history,
        prompt_version="240715-120000",
        system_prompt="You are a helpful AI assistant specializing in technology."
    )
    print(f"\nContext with history:")
    print(f"Current input: {context_with_history.user_input}")
    print(f"History length: {len(context_with_history.conversation_history)} messages")
    
    for i, msg in enumerate(context_with_history.conversation_history):
        print(f"  {i+1}. {msg.role}: {msg.content[:50]}...")
    
    # Validation examples
    try:
        invalid_context = PromptContext(
            user_input="",
            prompt_version="240715-120000",
            system_prompt="test"
        )
    except ValueError as e:
        print(f"\nValidation error (empty input): {e}")
    
    try:
        invalid_version = PromptContext(
            user_input="test",
            prompt_version="invalid-format",
            system_prompt="test"
        )
    except ValueError as e:
        print(f"Validation error (invalid version): {e}")
    
    print("PromptContext demonstration completed.")
