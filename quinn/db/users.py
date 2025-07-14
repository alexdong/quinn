import json
import logging
import time

from pydantic import BaseModel, Field

from quinn.db.database import get_db_connection

logger = logging.getLogger(__name__)


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
        logger.info("Creating user: id={user.id}, emails=%s", len(user.email_addresses))

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                sql = """
                    INSERT INTO users (id, created_at, updated_at, name, email_addresses, settings)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                params = (
                    user.id,
                    user.created_at,
                    user.updated_at,
                    user.name,
                    json.dumps(user.email_addresses),
                    json.dumps(user.settings) if user.settings else None,
                )
                logger.info("SQL: %s | Params: %s", sql.strip(), params)
                cursor.execute(sql, params)
                conn.commit()
                logger.debug("User created successfully: %s", user.id)
        except Exception as e:
            logger.error("Failed to create user {user.id}: %s", e)
            raise

    @staticmethod
    def get_by_id(user_id: str) -> User | None:
        """Retrieves a user by their ID."""
        logger.debug("Retrieving user by ID: %s", user_id)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT * FROM users WHERE id = ?"
                params = (user_id,)
                logger.info("SQL: %s | Params: %s", sql, params)
                cursor.execute(sql, params)
                row = cursor.fetchone()
                if row:
                    logger.debug("User found: %s", user_id)
                    return User(
                        id=row[0],
                        created_at=row[1],
                        updated_at=row[2],
                        name=row[3],
                        email_addresses=json.loads(row[4]),
                        settings=json.loads(row[5]) if row[5] else None,
                    )
                logger.debug("User not found: %s", user_id)
                return None
        except Exception as e:
            logger.error("Failed to retrieve user {user_id}: %s", e)
            raise

    @staticmethod
    def get_by_email(email: str) -> User | None:
        """Retrieves a user by any of their email addresses."""
        logger.debug("Retrieving user by email: %s", email)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT * FROM users"
                logger.info("SQL: %s", sql)
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    email_addresses = json.loads(row[4])
                    if email in email_addresses:
                        logger.debug("User found by email {email}: %s", row[0])
                        return User(
                            id=row[0],
                            created_at=row[1],
                            updated_at=row[2],
                            name=row[3],
                            email_addresses=email_addresses,
                            settings=json.loads(row[5]) if row[5] else None,
                        )
                logger.debug("No user found with email: %s", email)
                return None
        except Exception as e:
            logger.error("Failed to retrieve user by email {email}: %s", e)
            raise

    @staticmethod
    def update(user: User) -> None:
        """Updates an existing user."""
        user.updated_at = int(time.time())
        logger.info("Updating user: %s", user.id)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                sql = """
                    UPDATE users
                    SET updated_at = ?, name = ?, email_addresses = ?, settings = ?
                    WHERE id = ?
                    """
                params = (
                    user.updated_at,
                    user.name,
                    json.dumps(user.email_addresses),
                    json.dumps(user.settings) if user.settings else None,
                    user.id,
                )
                logger.info("SQL: %s | Params: %s", sql.strip(), params)
                cursor.execute(sql, params)
                conn.commit()
                logger.debug("User updated successfully: %s", user.id)
        except Exception as e:
            logger.error("Failed to update user {user.id}: %s", e)
            raise

    @staticmethod
    def add_alternative_email(user_id: str, email: str) -> bool:
        """Adds an alternative email address to an existing user.

        Returns True if email was added, False if user not found or email already exists.
        """
        logger.info("Adding alternative email {email} to user %s", user_id)

        try:
            user = Users.get_by_id(user_id)
            if not user:
                logger.warning("User not found for adding email: %s", user_id)
                return False

            if email in user.email_addresses:
                logger.debug("Email {email} already exists for user %s", user_id)
                return False  # Email already exists

            user.email_addresses.append(email)
            Users.update(user)
            logger.debug(
                "Alternative email {email} added successfully to user %s", user_id
            )
            return True
        except Exception as e:
            logger.error(
                "Failed to add alternative email {email} to user {user_id}: %s", e
            )
            raise

    @staticmethod
    def delete(user_id: str) -> None:
        """Deletes a user from the database."""
        logger.info("Deleting user: %s", user_id)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "DELETE FROM users WHERE id = ?"
                params = (user_id,)
                logger.info("SQL: %s | Params: %s", sql, params)
                cursor.execute(sql, params)
                rows_affected = cursor.rowcount
                conn.commit()
                if rows_affected > 0:
                    logger.debug("User deleted successfully: %s", user_id)
                else:
                    logger.warning("No user found to delete: %s", user_id)
        except Exception as e:
            logger.error("Failed to delete user {user_id}: %s", e)
            raise
