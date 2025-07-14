import json
import logging
import time

from pydantic import BaseModel, Field

from quinn.db.database import get_db_connection

logger = logging.getLogger(__name__)


class Conversation(BaseModel):
    id: str
    user_id: str
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: int = Field(default_factory=lambda: int(time.time()))
    title: str | None = None
    status: str = "active"
    total_cost: float = 0.0
    message_count: int = 0
    metadata: dict | None = None


class Conversations:
    @staticmethod
    def create(conversation: Conversation) -> None:
        """Creates a new conversation in the database."""
        logger.info(
            "Creating conversation: id={conversation.id}, user_id=%s",
            conversation.user_id,
        )

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                sql = """
                    INSERT INTO conversations (id, user_id, created_at, updated_at, title, status, total_cost, message_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                params = (
                    conversation.id,
                    conversation.user_id,
                    conversation.created_at,
                    conversation.updated_at,
                    conversation.title,
                    conversation.status,
                    conversation.total_cost,
                    conversation.message_count,
                    json.dumps(conversation.metadata)
                    if conversation.metadata
                    else None,
                )
                logger.info("SQL: %s | Params: %s", sql.strip(), params)
                cursor.execute(sql, params)
                conn.commit()
                logger.debug("Conversation created successfully: %s", conversation.id)
        except Exception as e:
            logger.error("Failed to create conversation {conversation.id}: %s", e)
            raise

    @staticmethod
    def get_by_id(conversation_id: str) -> Conversation | None:
        """Retrieves a conversation by its ID."""
        logger.debug("Retrieving conversation by ID: %s", conversation_id)

        try:
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
                        created_at=row[2],
                        updated_at=row[3],
                        title=row[4],
                        status=row[5],
                        total_cost=row[6],
                        message_count=row[7],
                        metadata=json.loads(row[8]) if row[8] else None,
                    )
                logger.debug("Conversation not found: %s", conversation_id)
                return None
        except Exception as e:
            logger.error("Failed to retrieve conversation {conversation_id}: %s", e)
            raise

    @staticmethod
    def get_by_user(user_id: str) -> list[Conversation]:
        """Retrieves all conversations for a given user."""
        logger.debug("Retrieving conversations for user: %s", user_id)

        try:
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
                        created_at=row[2],
                        updated_at=row[3],
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
        except Exception as e:
            logger.error("Failed to retrieve conversations for user {user_id}: %s", e)
            raise

    @staticmethod
    def update(conversation: Conversation) -> None:
        """Updates an existing conversation."""
        conversation.updated_at = int(time.time())
        logger.info("Updating conversation: %s", conversation.id)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                sql = """
                    UPDATE conversations
                    SET updated_at = ?, title = ?, status = ?, total_cost = ?, message_count = ?, metadata = ?
                    WHERE id = ?
                    """
                params = (
                    conversation.updated_at,
                    conversation.title,
                    conversation.status,
                    conversation.total_cost,
                    conversation.message_count,
                    json.dumps(conversation.metadata)
                    if conversation.metadata
                    else None,
                    conversation.id,
                )
                logger.info("SQL: %s | Params: %s", sql.strip(), params)
                cursor.execute(sql, params)
                conn.commit()
                logger.debug("Conversation updated successfully: %s", conversation.id)
        except Exception as e:
            logger.error("Failed to update conversation {conversation.id}: %s", e)
            raise

    @staticmethod
    def delete(conversation_id: str) -> None:
        """Deletes a conversation from the database."""
        logger.info("Deleting conversation: %s", conversation_id)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "DELETE FROM conversations WHERE id = ?"
                params = (conversation_id,)
                logger.info("SQL: %s | Params: %s", sql, params)
                cursor.execute(sql, params)
                rows_affected = cursor.rowcount
                conn.commit()
                if rows_affected > 0:
                    logger.debug(
                        "Conversation deleted successfully: %s", conversation_id
                    )
                else:
                    logger.warning(
                        "No conversation found to delete: %s", conversation_id
                    )
        except Exception as e:
            logger.error("Failed to delete conversation {conversation_id}: %s", e)
            raise
