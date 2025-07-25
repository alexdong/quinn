import json
from datetime import UTC, datetime

from quinn.db.database import get_db_connection
from quinn.models.conversation import Conversation
from quinn.utils.logging import get_logger, span_for_db

logger = get_logger(__name__)


class ConversationStore:
    @staticmethod
    def create(conversation: Conversation) -> None:
        """Creates a new conversation in the database."""
        span_for_db("conversations", conversation.id)
        logger.info(
            "Creating conversation: id=%s, user_id=%s",
            conversation.id,
            conversation.user_id,
        )

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = """
                INSERT INTO conversations (id, user_id, created_at, updated_at, title, status, total_cost, message_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
            params = (
                conversation.id,
                conversation.user_id,
                int(conversation.created_at.timestamp()),
                int(conversation.updated_at.timestamp()),
                conversation.title,
                conversation.status,
                conversation.total_cost,
                conversation.message_count,
                json.dumps(conversation.metadata) if conversation.metadata else None,
            )
            logger.info("SQL: %s | Params: %s", sql.strip(), params)
            cursor.execute(sql, params)
            assert cursor.rowcount == 1, (
                f"Failed to insert conversation {conversation.id}"
            )
            conn.commit()
            logger.debug("Conversation created successfully: %s", conversation.id)

    @staticmethod
    def get_by_id(conversation_id: str) -> Conversation | None:
        """Retrieves a conversation by its ID."""
        span_for_db("conversations", conversation_id)
        logger.debug("Retrieving conversation by ID: %s", conversation_id)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM conversations WHERE id = ?"
            params = (conversation_id,)
            logger.info("SQL: %s | Params: %s", sql, params)
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row:
                logger.debug("Conversation found: %s", conversation_id)
                return Conversation(
                    id=row[0],
                    user_id=row[1],
                    created_at=datetime.fromtimestamp(row[2], UTC),
                    updated_at=datetime.fromtimestamp(row[3], UTC),
                    title=row[4],
                    status=row[5],
                    total_cost=row[6],
                    message_count=row[7],
                    metadata=json.loads(row[8]) if row[8] else None,
                )
            logger.debug("Conversation not found: %s", conversation_id)
            return None

    @staticmethod
    def get_by_user(user_id: str) -> list[Conversation]:
        """Retrieves all conversations for a given user."""
        span_for_db("users", user_id)
        logger.debug("Retrieving conversations for user: %s", user_id)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM conversations WHERE user_id = ?"
            params = (user_id,)
            logger.info("SQL: %s | Params: %s", sql, params)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conversations = [
                Conversation(
                    id=row[0],
                    user_id=row[1],
                    created_at=datetime.fromtimestamp(row[2], UTC),
                    updated_at=datetime.fromtimestamp(row[3], UTC),
                    title=row[4],
                    status=row[5],
                    total_cost=row[6],
                    message_count=row[7],
                    metadata=json.loads(row[8]) if row[8] else None,
                )
                for row in rows
            ]
            logger.debug(
                "Found {len(conversations)} conversations for user %s", user_id
            )
            return conversations

    @staticmethod
    def update(conversation: Conversation) -> None:
        """Updates an existing conversation."""
        span_for_db("conversations", conversation.id)
        conversation.updated_at = datetime.now(UTC)
        logger.info("Updating conversation: %s", conversation.id)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = """
                UPDATE conversations
                SET updated_at = ?, title = ?, status = ?, total_cost = ?, message_count = ?, metadata = ?
                WHERE id = ?
                """
            params = (
                int(conversation.updated_at.timestamp()),
                conversation.title,
                conversation.status,
                conversation.total_cost,
                conversation.message_count,
                json.dumps(conversation.metadata) if conversation.metadata else None,
                conversation.id,
            )
            logger.info("SQL: %s | Params: %s", sql.strip(), params)
            cursor.execute(sql, params)
            assert cursor.rowcount == 1, (
                f"Failed to update conversation {conversation.id}"
            )
            conn.commit()
            logger.debug("Conversation updated successfully: %s", conversation.id)

    @staticmethod
    def delete(conversation_id: str) -> None:
        """Deletes a conversation from the database."""
        span_for_db("conversations", conversation_id)
        logger.info("Deleting conversation: %s", conversation_id)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = "DELETE FROM conversations WHERE id = ?"
            params = (conversation_id,)
            logger.info("SQL: %s | Params: %s", sql, params)
            cursor.execute(sql, params)
            rows_affected = cursor.rowcount
            conn.commit()
            if rows_affected > 0:
                logger.debug("Conversation deleted successfully: %s", conversation_id)
            else:
                logger.warning("No conversation found to delete: %s", conversation_id)
