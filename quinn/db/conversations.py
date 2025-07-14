import json
import time

from pydantic import BaseModel, Field

from quinn.db.database import get_db_connection


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
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversations (id, user_id, created_at, updated_at, title, status, total_cost, message_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
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
                ),
            )
            conn.commit()

    @staticmethod
    def get_by_id(conversation_id: str) -> Conversation | None:
        """Retrieves a conversation by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            )
            row = cursor.fetchone()
            if row:
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
            return None

    @staticmethod
    def get_by_user(user_id: str) -> list[Conversation]:
        """Retrieves all conversations for a given user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            return [
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

    @staticmethod
    def update(conversation: Conversation) -> None:
        """Updates an existing conversation."""
        conversation.updated_at = int(time.time())
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE conversations
                SET updated_at = ?, title = ?, status = ?, total_cost = ?, message_count = ?, metadata = ?
                WHERE id = ?
                """,
                (
                    conversation.updated_at,
                    conversation.title,
                    conversation.status,
                    conversation.total_cost,
                    conversation.message_count,
                    json.dumps(conversation.metadata)
                    if conversation.metadata
                    else None,
                    conversation.id,
                ),
            )
            conn.commit()

    @staticmethod
    def delete(conversation_id: str) -> None:
        """Deletes a conversation from the database."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            conn.commit()
