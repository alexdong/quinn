import json
import logging
from datetime import UTC, datetime

from quinn.db.database import get_db_connection
from quinn.models.user import User

logger = logging.getLogger(__name__)


class Users:
    @staticmethod
    def create(user: User) -> None:
        """Creates a new user in the database."""
        logger.info(
            "Creating user: id=%s, emails=%s", user.id, len(user.email_addresses)
        )

        try:
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
                conn.commit()
                logger.debug("User created successfully: %s", user.id)
        except Exception as e:
            logger.error("Failed to create user %s: %s", user.id, e)
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
                        created_at=datetime.fromtimestamp(row[1], UTC),
                        updated_at=datetime.fromtimestamp(row[2], UTC),
                        name=row[3],
                        email_addresses=json.loads(row[4]),
                        settings=json.loads(row[5]) if row[5] else None,
                    )
                logger.debug("User not found: %s", user_id)
                return None
        except Exception as e:
            logger.error("Failed to retrieve user %s: %s", user_id, e)
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
        except Exception as e:
            logger.error("Failed to retrieve user by email %s: %s", email, e)
            raise

    @staticmethod
    def update(user: User) -> None:
        """Updates an existing user."""
        user.updated_at = datetime.now(UTC)
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
                    int(user.updated_at.timestamp()),
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
            logger.error("Failed to update user %s: %s", user.id, e)
            raise

    @staticmethod
    def add_alternative_email(user_id: str, email: str) -> bool:
        """Adds an alternative email address to an existing user.

        Returns True if email was added, False if user not found or email already exists.
        """
        logger.info("Adding alternative email %s to user %s", email, user_id)

        try:
            user = Users.get_by_id(user_id)
            if not user:
                logger.warning("User not found for adding email: %s", user_id)
                return False

            if email in user.email_addresses:
                logger.debug("Email %s already exists for user %s", email, user_id)
                return False  # Email already exists

            user.email_addresses.append(email)
            Users.update(user)
            logger.debug(
                "Alternative email %s added successfully to user %s", email, user_id
            )
            return True
        except Exception as e:
            logger.error(
                "Failed to add alternative email %s to user %s: %s", email, user_id, e
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
            logger.error("Failed to delete user %s: %s", user_id, e)
            raise
