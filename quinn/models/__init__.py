"""Data models for Quinn AI agent."""

from .config import AgentConfig
from .conversation import Conversation, Message
from .prompt import PromptContext
from .response import AgentResponse, ConversationMetrics

# Rebuild models to resolve forward references
PromptContext.model_rebuild()
Conversation.model_rebuild()

__all__ = [
    "AgentConfig",
    "AgentResponse",
    "Conversation",
    "ConversationMetrics",
    "Message",
    "PromptContext",
]
