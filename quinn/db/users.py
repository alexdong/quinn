import json
from datetime import UTC, datetime

from quinn.db.database import get_db_connection
from quinn.models.user import User
from quinn.utils.logging import get_logger, span_for_db

logger = get_logger(__name__)


class UserStore:
    @staticmethod
    def create(user: User) -> None:
        """Creates a new user in the database."""
        span_for_db("users", user.id)
        logger.info(
            "Creating user: id=%s, emails=%s", user.id, len(user.email_addresses)
        )

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = """
                INSERT INTO users (id, created_at, updated_at, name, email_addresses, settings)
                VALUES (?, ?, ?, ?, ?, ?)
                """
            params = (
                user.id,
                int(user.created_at.timestamp()),
                int(user.updated_at.timestamp()),
                user.name,
                json.dumps(user.email_addresses),
                json.dumps(user.settings) if user.settings else None,
            )
            logger.info("SQL: %s | Params: %s", sql.strip(), params)
            cursor.execute(sql, params)
            assert cursor.rowcount == 1, f"Failed to insert user {user.id}"
            conn.commit()
            logger.debug("User created successfully: %s", user.id)

    @staticmethod
    def get_by_id(user_id: str) -> User | None:
        """Retrieves a user by their ID."""
        span_for_db("users", user_id)
        logger.debug("Retrieving user by ID: %s", user_id)

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
                    created_at=datetime.fromtimestamp(row[1], UTC),
                    updated_at=datetime.fromtimestamp(row[2], UTC),
                    name=row[3],
                    email_addresses=json.loads(row[4]),
                    settings=json.loads(row[5]) if row[5] else None,
                )
            logger.debug("User not found: %s", user_id)
            return None

    @staticmethod
    def get_by_email(email: str) -> User | None:
        """Retrieves a user by any of their email addresses."""
        span_for_db("users", email)
        logger.debug("Retrieving user by email: %s", email)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM users"
            logger.info("SQL: %s", sql)
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                email_addresses = json.loads(row[4])
                if email in email_addresses:
                    logger.debug("User found by email %s: %s", email, row[0])
                    return User(
                        id=row[0],
                        created_at=datetime.fromtimestamp(row[1], UTC),
                        updated_at=datetime.fromtimestamp(row[2], UTC),
                        name=row[3],
                        email_addresses=email_addresses,
                        settings=json.loads(row[5]) if row[5] else None,
                    )
            logger.debug("No user found with email: %s", email)
            return None

    @staticmethod
    def update(user: User) -> None:
        """Updates an existing user."""
        span_for_db("users", user.id)
        user.updated_at = datetime.now(UTC)
        logger.info("Updating user: %s", user.id)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = """
                UPDATE users
                SET updated_at = ?, name = ?, email_addresses = ?, settings = ?
                WHERE id = ?
                """
            params = (
                int(user.updated_at.timestamp()),
                user.name,
                json.dumps(user.email_addresses),
                json.dumps(user.settings) if user.settings else None,
                user.id,
            )
            logger.info("SQL: %s | Params: %s", sql.strip(), params)
            cursor.execute(sql, params)
            assert cursor.rowcount == 1, f"Failed to update user {user.id}"
            conn.commit()
            logger.debug("User updated successfully: %s", user.id)

    @staticmethod
    def add_alternative_email(user_id: str, email: str) -> bool:
        """Adds an alternative email address to an existing user.

        Returns True if email was added, False if user not found or email already exists.
        """
        span_for_db("users", user_id)
        logger.info("Adding alternative email %s to user %s", email, user_id)

        user = UserStore.get_by_id(user_id)
        if not user:
            logger.warning("User not found for adding email: %s", user_id)
            return False

        if email in user.email_addresses:
            logger.debug("Email %s already exists for user %s", email, user_id)
            return False  # Email already exists

        user.email_addresses.append(email)
        UserStore.update(user)
        logger.debug(
            "Alternative email %s added successfully to user %s", email, user_id
        )
        return True

    @staticmethod
    def delete(user_id: str) -> None:
        """Deletes a user from the database."""
        span_for_db("users", user_id)
        logger.info("Deleting user: %s", user_id)

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
