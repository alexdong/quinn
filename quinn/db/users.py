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
    def get_by_email(email: str) -> User | None:
        """Retrieves a user by any of their email addresses."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            for row in rows:
                email_addresses = json.loads(row[4])
                if email in email_addresses:
                    return User(
                        id=row[0],
                        created_at=row[1],
                        updated_at=row[2],
                        name=row[3],
                        email_addresses=email_addresses,
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
    def add_alternative_email(user_id: str, email: str) -> bool:
        """Adds an alternative email address to an existing user.
        
        Returns True if email was added, False if user not found or email already exists.
        """
        user = Users.get_by_id(user_id)
        if not user:
            return False
        
        if email in user.email_addresses:
            return False  # Email already exists
        
        user.email_addresses.append(email)
        Users.update(user)
        return True

    @staticmethod
    def delete(user_id: str) -> None:
        """Deletes a user from the database."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
