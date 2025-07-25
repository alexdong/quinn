"""Conversation management functionality shared between CLI and Web interfaces."""

from typing import NamedTuple
from uuid import uuid4

from quinn.agent.core import generate_response
from quinn.db.conversations import ConversationStore
from quinn.db.database import create_tables
from quinn.db.messages import MessageStore
from quinn.db.users import UserStore
from quinn.models.config import AgentConfig
from quinn.models.conversation import Conversation
from quinn.models.message import Message
from quinn.models.user import User
from quinn.utils.logging import get_logger

logger = get_logger(__name__)

# Constants
TITLE_MAX_LENGTH = 50
TITLE_TRUNCATE_LENGTH = 47


class ConversationResponse(NamedTuple):
    """Response from conversation operations."""

    message: Message
    conversation: Conversation


class ConversationManager:
    """Manages conversations and message operations."""

    @staticmethod
    def setup_database() -> None:
        """Create database tables if they don't exist."""
        try:
            create_tables()
        except Exception as e:
            # Silently ignore if tables already exist
            if "already exists" not in str(e):
                raise

    @staticmethod
    def ensure_user(user_id: str, name: str, email_addresses: list[str]) -> None:
        """Create user if it doesn't exist."""
        try:
            if not UserStore.get_by_id(user_id):
                user = User(
                    id=user_id,
                    name=name,
                    email_addresses=email_addresses,
                )
                UserStore.create(user)
        except Exception as e:
            # Silently ignore if user already exists
            if "already exists" not in str(e):
                raise

    @staticmethod
    def get_model_config(model: str) -> AgentConfig:
        """Get the model configuration for the given model name."""
        model_configs = {
            "gemini-2.5-flash": AgentConfig.gemini25flash,
            "gemini-2.5-flash-thinking": AgentConfig.gemini25flashthinking,
            "claude-sonnet-4": AgentConfig.sonnet4,
            "gpt-4o-mini": AgentConfig.o4mini,
            "gpt-4.1": AgentConfig.gpt41,
            "gpt-4.1-mini": AgentConfig.gpt41mini,
        }

        if model not in model_configs:
            available_models = ", ".join(model_configs.keys())
            msg = f"Unsupported model '{model}'. Available models: {available_models}"
            raise ValueError(msg)

        return model_configs[model]()

    @staticmethod
    def get_available_models() -> list[str]:
        """Get list of available model names."""
        return [
            "gemini-2.5-flash",
            "gemini-2.5-flash-thinking",
            "claude-sonnet-4",
            "gpt-4o-mini",
            "gpt-4.1",
            "gpt-4.1-mini",
        ]

    @staticmethod
    def list_conversations(user_id: str) -> list[Conversation]:
        """List all conversations for a user, sorted by updated_at descending."""
        conversations = ConversationStore.get_by_user(user_id)
        conversations.sort(key=lambda x: x.updated_at, reverse=True)
        return conversations

    @staticmethod
    def get_conversation_by_index(user_id: str, index: int) -> Conversation | None:
        """Get conversation by 1-based index (as shown in list)."""
        conversations = ConversationManager.list_conversations(user_id)
        if not conversations or index < 1 or index > len(conversations):
            return None
        return conversations[index - 1]  # Convert to 0-based index

    @staticmethod
    def get_most_recent_conversation(user_id: str) -> Conversation | None:
        """Get the most recently updated conversation."""
        conversations = ConversationManager.list_conversations(user_id)
        return conversations[0] if conversations else None

    @staticmethod
    def build_conversation_context(conversation_id: str, user_input: str) -> str:
        """Build conversation context with previous messages."""
        existing_messages = MessageStore.get_by_conversation(conversation_id)

        # Build conversation history for context
        conversation_history = []
        for msg in existing_messages:
            conversation_history.append(f"User: {msg.user_content}")
            conversation_history.append(f"Quinn: {msg.assistant_content}")

        # Add conversation history as context
        if conversation_history:
            context = "\\n\\n".join(conversation_history)
            return f"Previous conversation:\\n{context}\\n\\nNew message: {user_input}"

        return user_input

    @staticmethod
    async def create_new_conversation(
        user_id: str, user_content: str, model: str
    ) -> ConversationResponse:
        """Create a new conversation with initial message."""
        conversation_id = str(uuid4())

        # Create user message
        user_message = Message(
            conversation_id=conversation_id,
            user_content=user_content,
            system_prompt="",
        )

        config = ConversationManager.get_model_config(model)

        # Generate response
        response_message = await generate_response(user_message, config=config)

        # Create conversation record
        title = (
            user_content[:TITLE_MAX_LENGTH] + "..."
            if len(user_content) > TITLE_MAX_LENGTH
            else user_content
        )
        conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            title=title,
        )
        ConversationStore.create(conversation)

        # Save message to database
        MessageStore.create(response_message, user_id)

        return ConversationResponse(response_message, conversation)

    @staticmethod
    async def continue_conversation(
        conversation_id: str, user_id: str, user_input: str, model: str
    ) -> ConversationResponse:
        """Continue an existing conversation with new user input."""
        # Create new user message with context
        user_message = Message(
            conversation_id=conversation_id,
            user_content=ConversationManager.build_conversation_context(
                conversation_id, user_input
            ),
            system_prompt="",  # Use default system prompt
        )

        config = ConversationManager.get_model_config(model)

        # Generate response
        response_message = await generate_response(user_message, config=config)

        # Update conversation message count and cost
        conversation = ConversationStore.get_by_id(conversation_id)
        if conversation:
            conversation.message_count += 1
            if response_message.metadata:
                conversation.total_cost += response_message.metadata.cost_usd
            ConversationStore.update(conversation)

        # Save message to database
        MessageStore.create(response_message, user_id)

        # Ensure we have a conversation object for the response
        assert conversation is not None, f"Conversation {conversation_id} not found"
        return ConversationResponse(response_message, conversation)

    @staticmethod
    def get_conversation_messages(conversation_id: str) -> list[Message]:
        """Get all messages for a conversation."""
        return MessageStore.get_by_conversation(conversation_id)

    @staticmethod
    def get_last_assistant_message(conversation_id: str) -> str | None:
        """Get the last assistant message from a conversation."""
        messages = ConversationManager.get_conversation_messages(conversation_id)
        if not messages:
            return None

        # Get the most recent message's assistant content
        last_message = messages[-1]
        return (
            last_message.assistant_content if last_message.assistant_content else None
        )
