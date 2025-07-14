import json
import time

from pydantic import BaseModel, Field

from quinn.db.database import get_db_connection


class User(BaseModel):
    id: str
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: int = Field(default_factory=lambda: int(time.time()))
    name: str | None = None
    email_addresses: list[str]
    settings: dict | None = None


class Users:
    @staticmethod
    def create(user: User) -> None:
        """Creates a new user in the database."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (id, created_at, updated_at, name, email_addresses, settings)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user.id,
                    user.created_at,
                    user.updated_at,
                    user.name,
                    json.dumps(user.email_addresses),
                    json.dumps(user.settings) if user.settings else None,
                ),
            )
            conn.commit()

    @staticmethod
    def get_by_id(user_id: str) -> User | None:
        """Retrieves a user by their ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    created_at=row[1],
                    updated_at=row[2],
                    name=row[3],
                    email_addresses=json.loads(row[4]),
                    settings=json.loads(row[5]) if row[5] else None,
                )
            return None

    @staticmethod
    def update(user: User) -> None:
        """Updates an existing user."""
        user.updated_at = int(time.time())
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET updated_at = ?, name = ?, email_addresses = ?, settings = ?
                WHERE id = ?
                """,
                (
                    user.updated_at,
                    user.name,
                    json.dumps(user.email_addresses),
                    json.dumps(user.settings) if user.settings else None,
                    user.id,
                ),
            )
            conn.commit()

    @staticmethod
    def delete(user_id: str) -> None:
        """Deletes a user from the database."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
