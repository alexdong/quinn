"""Data models for Quinn AI agent."""

from .config import AgentConfig
from .conversation import Conversation, ConversationMetrics, Message
from .email import EmailAttachment, EmailDirection, EmailMessage
from .message import MessageMetrics
from .types import PROMPT_VERSION

# Rebuild models to resolve forward references
Conversation.model_rebuild()

__all__ = [
    "PROMPT_VERSION",
    "AgentConfig",
    "Conversation",
    "ConversationMetrics",
    "EmailAttachment",
    "EmailDirection",
    "EmailMessage",
    "Message",
    "MessageMetrics",
]
