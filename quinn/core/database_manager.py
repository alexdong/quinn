"""Database management functionality shared between interfaces."""

from pathlib import Path

from quinn.db.database import DATABASE_FILE
from quinn.utils.logging import get_logger

from .conversation_manager import ConversationManager

logger = get_logger(__name__)


class DatabaseManager:
    """Manages database setup and operations."""

    @staticmethod
    def setup_database() -> None:
        """Ensure database tables exist and create default users if needed."""
        try:
            ConversationManager.setup_database()
        except Exception as e:
            logger.error("Database setup failed: %s", e)
            raise

    @staticmethod
    def ensure_cli_user() -> None:
        """Create CLI user if it doesn't exist."""
        ConversationManager.ensure_user(
            user_id="cli-user", name="CLI User", email_addresses=["cli@localhost"]
        )

    @staticmethod
    def ensure_web_user() -> None:
        """Create web user if it doesn't exist."""
        ConversationManager.ensure_user(
            user_id="web-user", name="Web User", email_addresses=["web@localhost"]
        )

    @staticmethod
    def reset_all() -> None:
        """Remove all conversations and recreate a fresh database."""
        try:
            Path(DATABASE_FILE).unlink(missing_ok=True)
            DatabaseManager.setup_database()
            logger.info("All conversations reset.")
        except Exception as e:
            logger.error("Failed to reset conversations: %s", e)
            raise
