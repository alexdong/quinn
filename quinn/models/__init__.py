"""Data models for Quinn AI agent."""

from .config import AgentConfig
from .conversation import Conversation, Message
from .response import ConversationMetrics, MessageMetrics
from .types import PROMPT_VERSION

# Rebuild models to resolve forward references
Conversation.model_rebuild()

__all__ = [
    "PROMPT_VERSION",
    "AgentConfig",
    "Conversation",
    "ConversationMetrics",
    "Message",
    "MessageMetrics",
]
