import json
import logging
import time

from pydantic import BaseModel, Field

from quinn.db.database import get_db_connection

logger = logging.getLogger(__name__)


class Message(BaseModel):
    id: str
    conversation_id: str
    user_id: str
    created_at: int = Field(default_factory=lambda: int(time.time()))
    last_updated_at: int = Field(default_factory=lambda: int(time.time()))
    system_prompt: str = ""
    user_content: str = ""
    assistant_content: str = ""
    metadata: dict | None = None


class Messages:
    @staticmethod
    def create(message: Message) -> None:
        """Creates a new message in the database."""
        logger.info(
            "Creating message: id={message.id}, conversation_id=%s",
            message.conversation_id,
        )

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO messages (id, conversation_id, user_id, created_at, last_updated_at, system_prompt, user_content, assistant_content, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        message.id,
                        message.conversation_id,
                        message.user_id,
                        message.created_at,
                        message.last_updated_at,
                        message.system_prompt,
                        message.user_content,
                        message.assistant_content,
                        json.dumps(message.metadata) if message.metadata else None,
                    ),
                )
                conn.commit()
                logger.debug("Message created successfully: %s", message.id)
        except Exception as e:
            logger.error("Failed to create message {message.id}: %s", e)
            raise

    @staticmethod
    def get_by_id(message_id: str) -> Message | None:
        """Retrieves a message by its ID."""
        logger.debug("Retrieving message by ID: %s", message_id)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
                row = cursor.fetchone()
                if row:
                    logger.debug("Message found: %s", message_id)
                    return Message(
                        id=row[0],
                        conversation_id=row[1],
                        user_id=row[2],
                        created_at=row[3],
                        last_updated_at=row[4],
                        system_prompt=row[5],
                        user_content=row[6],
                        assistant_content=row[7],
                        metadata=json.loads(row[8]) if row[8] else None,
                    )
                logger.debug("Message not found: %s", message_id)
                return None
        except Exception as e:
            logger.error("Failed to retrieve message {message_id}: %s", e)
            raise

    @staticmethod
    def get_by_conversation(conversation_id: str) -> list[Message]:
        """Retrieves all messages for a given conversation."""
        logger.debug("Retrieving messages for conversation: %s", conversation_id)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
                    (conversation_id,),
                )
                rows = cursor.fetchall()
                messages = [
                    Message(
                        id=row[0],
                        conversation_id=row[1],
                        user_id=row[2],
                        created_at=row[3],
                        last_updated_at=row[4],
                        system_prompt=row[5],
                        user_content=row[6],
                        assistant_content=row[7],
                        metadata=json.loads(row[8]) if row[8] else None,
                    )
                    for row in rows
                ]
                logger.debug(
                    "Found {len(messages)} messages for conversation %s",
                    conversation_id,
                )
                return messages
        except Exception as e:
            logger.error(
                "Failed to retrieve messages for conversation {conversation_id}: %s", e
            )
            raise

    @staticmethod
    def update(message: Message) -> None:
        """Updates an existing message."""
        message.last_updated_at = int(time.time())
        logger.info("Updating message: %s", message.id)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE messages
                    SET last_updated_at = ?, system_prompt = ?, user_content = ?, assistant_content = ?, metadata = ?
                    WHERE id = ?
                    """,
                    (
                        message.last_updated_at,
                        message.system_prompt,
                        message.user_content,
                        message.assistant_content,
                        json.dumps(message.metadata) if message.metadata else None,
                        message.id,
                    ),
                )
                conn.commit()
                logger.debug("Message updated successfully: %s", message.id)
        except Exception as e:
            logger.error("Failed to update message {message.id}: %s", e)
            raise

    @staticmethod
    def delete(message_id: str) -> None:
        """Deletes a message from the database."""
        logger.info("Deleting message: %s", message_id)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
                rows_affected = cursor.rowcount
                conn.commit()
                if rows_affected > 0:
                    logger.debug("Message deleted successfully: %s", message_id)
                else:
                    logger.warning("No message found to delete: %s", message_id)
        except Exception as e:
            logger.error("Failed to delete message {message_id}: %s", e)
            raise
