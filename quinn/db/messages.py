import json
from datetime import UTC, datetime

from quinn.db.database import get_db_connection
from quinn.models.message import Message, MessageMetrics
from quinn.utils.logging import get_logger, span_for_db

logger = get_logger(__name__)


class MessageStore:
    @staticmethod
    def create(message: Message, user_id: str) -> None:
        """Creates a new message in the database."""
        span_for_db("messages", message.id)
        logger.info(
            "Creating message: id=%s, conversation_id=%s",
            message.id,
            message.conversation_id,
        )

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = """
                INSERT INTO messages (id, conversation_id, user_id, created_at, last_updated_at, system_prompt, user_content, assistant_content, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
            params = (
                message.id,
                message.conversation_id,
                user_id,
                int(message.created_at.timestamp()),
                int(message.last_updated_at.timestamp()),
                message.system_prompt,
                message.user_content,
                message.assistant_content,
                json.dumps(message.metadata.model_dump()) if message.metadata else None,
            )
            logger.info("SQL: %s | Params: %s", sql.strip(), params)
            cursor.execute(sql, params)
            assert cursor.rowcount == 1, f"Failed to insert message {message.id}"
            conn.commit()
            logger.debug("Message created successfully: %s", message.id)

    @staticmethod
    def get_by_id(message_id: str) -> Message | None:
        """Retrieves a message by its ID."""
        span_for_db("messages", message_id)
        logger.debug("Retrieving message by ID: %s", message_id)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM messages WHERE id = ?"
            params = (message_id,)
            logger.info("SQL: %s | Params: %s", sql, params)
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row:
                logger.debug("Message found: %s", message_id)
                metadata = None
                if row[8]:
                    metadata_dict = json.loads(row[8])
                    metadata = MessageMetrics(**metadata_dict)

                return Message(
                    id=row[0],
                    conversation_id=row[1],
                    created_at=datetime.fromtimestamp(row[3], UTC),
                    last_updated_at=datetime.fromtimestamp(row[4], UTC),
                    system_prompt=row[5],
                    user_content=row[6],
                    assistant_content=row[7],
                    metadata=metadata,
                )
            logger.debug("Message not found: %s", message_id)
            return None

    @staticmethod
    def get_by_conversation(conversation_id: str) -> list[Message]:
        """Retrieves all messages for a given conversation."""
        span_for_db("conversations", conversation_id)
        logger.debug("Retrieving messages for conversation: %s", conversation_id)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC"
            params = (conversation_id,)
            logger.info("SQL: %s | Params: %s", sql, params)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            messages = []
            for row in rows:
                metadata = None
                if row[8]:
                    metadata_dict = json.loads(row[8])
                    metadata = MessageMetrics(**metadata_dict)

                message = Message(
                    id=row[0],
                    conversation_id=row[1],
                    created_at=datetime.fromtimestamp(row[3], UTC),
                    last_updated_at=datetime.fromtimestamp(row[4], UTC),
                    system_prompt=row[5],
                    user_content=row[6],
                    assistant_content=row[7],
                    metadata=metadata,
                )
                messages.append(message)

            logger.debug(
                "Found %d messages for conversation %s",
                len(messages),
                conversation_id,
            )
            return messages

    @staticmethod
    def update(message: Message) -> None:
        """Updates an existing message."""
        span_for_db("messages", message.id)
        # Update the last_updated_at timestamp
        message.last_updated_at = datetime.now(UTC)
        logger.info("Updating message: %s", message.id)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = """
                UPDATE messages
                SET last_updated_at = ?, system_prompt = ?, user_content = ?, assistant_content = ?, metadata = ?
                WHERE id = ?
                """
            params = (
                int(message.last_updated_at.timestamp()),
                message.system_prompt,
                message.user_content,
                message.assistant_content,
                json.dumps(message.metadata.model_dump()) if message.metadata else None,
                message.id,
            )
            logger.info("SQL: %s | Params: %s", sql.strip(), params)
            cursor.execute(sql, params)
            assert cursor.rowcount == 1, f"Failed to update message {message.id}"
            conn.commit()
            logger.debug("Message updated successfully: %s", message.id)

    @staticmethod
    def delete(message_id: str) -> None:
        """Deletes a message from the database."""
        span_for_db("messages", message_id)
        logger.info("Deleting message: %s", message_id)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = "DELETE FROM messages WHERE id = ?"
            params = (message_id,)
            logger.info("SQL: %s | Params: %s", sql, params)
            cursor.execute(sql, params)
            rows_affected = cursor.rowcount
            conn.commit()
            if rows_affected > 0:
                logger.debug("Message deleted successfully: %s", message_id)
            else:
                logger.warning("No message found to delete: %s", message_id)
