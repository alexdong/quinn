import json
import time

from pydantic import BaseModel, Field

from quinn.db.database import get_db_connection


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

    @staticmethod
    def get_by_id(message_id: str) -> Message | None:
        """Retrieves a message by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
            row = cursor.fetchone()
            if row:
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
            return None

    @staticmethod
    def get_by_conversation(conversation_id: str) -> list[Message]:
        """Retrieves all messages for a given conversation."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
                (conversation_id,),
            )
            rows = cursor.fetchall()
            return [
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

    @staticmethod
    def update(message: Message) -> None:
        """Updates an existing message."""
        message.last_updated_at = int(time.time())
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

    @staticmethod
    def delete(message_id: str) -> None:
        """Deletes a message from the database."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
            conn.commit()
